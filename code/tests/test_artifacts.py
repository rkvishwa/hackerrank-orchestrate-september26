from __future__ import annotations

import csv
import json
import os
import stat
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

import pytest

from buy_or_wait.artifacts.evaluation import validate_output, normalize
from buy_or_wait.artifacts.bundle import publish, sha256
from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.llm.usage import UsageTracker
from test_correctness import setup, DAY


def engine(tmp_path):
    ds, p, q = setup()
    settings = Settings(llm_enabled=False, deterministic_mode=True, evidence_cache_dir=tmp_path / "cache",
                        output_path=tmp_path / "output.csv", report_dir=tmp_path / "evaluation")
    return DecisionEngine(ds, settings)


def test_numeric_sample_comparison_is_structural():
    assert normalize("amount_safe_to_pay", "100.00") == normalize("amount_safe_to_pay", "100")
    assert normalize("payment_plan", "2026-01-01:100.00") == normalize("payment_plan", "2026-01-01:100")


def test_usage_is_scoped_and_unknown_price_is_not_zero():
    with UsageTracker.scoped({"model": (2.0, 8.0)}) as first:
        first.record("model", 1000, 500)
        assert first.summary(10)["estimated_total_cost_usd"] == pytest.approx(0.006)
        assert first.summary(10)["estimated_cost_per_request_usd"] == pytest.approx(0.0006)
        with UsageTracker.scoped() as second:
            assert second.summary(10)["total_calls"] == 0
            second.record("unpriced", 10, 5)
            assert second.summary(10)["estimated_total_cost_usd"] is None
        assert UsageTracker.instance() is first
    with UsageTracker.scoped() as third:
        assert third.summary(10)["total_tokens"] == 0


def test_csv_duplicate_unknown_and_malformed_rows_rejected(tmp_path):
    e = engine(tmp_path)
    result = e.decide(e.dataset.requests[0])
    path = tmp_path / "output.csv"
    e.write_output([result, result], path)
    assert any("duplicate" in error for error in validate_output(path, e))
    e.write_output([replace(result, request_id="unknown")], path)
    assert any("unknown" in error for error in validate_output(path, e))
    path.write_text("wrong,header\n", encoding="utf-8")
    assert validate_output(path, e)


def test_failed_validation_preserves_previous_artifacts(tmp_path, monkeypatch):
    e = engine(tmp_path)
    output = e.settings.resolved_output_path
    output.write_text("previous output", encoding="utf-8")
    invalid = replace(e.decide(e.dataset.requests[0]), amount_safe_to_pay=D("999"))
    with UsageTracker.scoped() as tracker, pytest.raises(ValueError, match="validation failed"):
        publish(e, [invalid], e.settings, tracker, ["r"])
    assert output.read_text() == "previous output"
    assert not (e.settings.resolved_report_dir / "evaluation_report.json").exists()


def test_bundle_hashes_and_report_values_match(tmp_path, monkeypatch):
    e = engine(tmp_path)
    monkeypatch.setattr("buy_or_wait.artifacts.bundle.score_samples", lambda *a: {"available": False})
    e.settings.dataset_dir = tmp_path
    result = e.decide(e.dataset.requests[0])
    with UsageTracker.scoped() as tracker:
        output = publish(e, [result], e.settings, tracker, ["r"])
    metadata = json.loads((e.settings.resolved_report_dir / "evaluation_report.json").read_text())
    assert metadata["output_sha256"] == sha256(output)
    assert metadata["usage"]["request_count"] == 1
    assert metadata["contract_errors"] == []
    assert metadata["hidden_dataset_accuracy"] == "unknown"
    assert metadata["run_id"] in (e.settings.resolved_report_dir / "usage_report.md").read_text()
    assert metadata["report_sha256"]["usage_report.md"] == sha256(e.settings.resolved_report_dir / "usage_report.md")
    if os.name != "nt":
        for name in ("usage_report.md", "evaluation_report.md", "evaluation_report.json"):
            assert stat.S_IMODE((e.settings.resolved_report_dir / name).stat().st_mode) == 0o644
    (e.settings.resolved_report_dir / "usage_report.md").write_text("tampered")
    assert metadata["report_sha256"]["usage_report.md"] != sha256(e.settings.resolved_report_dir / "usage_report.md")
