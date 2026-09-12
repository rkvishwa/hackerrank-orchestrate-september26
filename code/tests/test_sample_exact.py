from __future__ import annotations

import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import RequestRow, load_dataset
from buy_or_wait.artifacts.evaluation import SCORED_FIELDS, normalize

DATASET = Path(__file__).resolve().parents[2] / "dataset"


def _load_sample_requests() -> list[tuple[RequestRow, dict[str, str]]]:
    rows: list[tuple[RequestRow, dict[str, str]]] = []
    with (DATASET / "sample_requests.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            request = RequestRow(
                request_id=row["request_id"],
                user_id=row["user_id"],
                request_date=date.fromisoformat(row["request_date"]),
                request_type=row["request_type"],
                requested_amount=Decimal(row["requested_amount"]),
                desired_completion_date=date.fromisoformat(row["desired_completion_date"]),
                allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
                request_text=row["request_text"],
            )
            rows.append((request, row))
    return rows


@pytest.fixture(scope="module")
def engine():
    dataset = load_dataset(DATASET)
    return DecisionEngine(dataset, Settings(deterministic_mode=True, llm_enabled=False))


def test_sample_release_gate(engine):
    samples = _load_sample_requests()
    hits = dict.fromkeys(SCORED_FIELDS, 0)
    error = Decimal("0")
    for request, label in samples:
        result = engine.decide(request)
        for field in SCORED_FIELDS:
            hits[field] += normalize(field, getattr(result, field)) == normalize(field, label[field])
        error += abs(result.amount_safe_to_pay - Decimal(label["amount_safe_to_pay"])) / request.requested_amount
    baseline = json.loads((Path(__file__).resolve().parents[1] / "evaluation" / "reference_baseline.json").read_text())["samples"]
    regressions = [f"{f}: {baseline['matches'][f]} -> {hits[f]}" for f in SCORED_FIELDS
                   if hits[f] < baseline["matches"][f]]
    assert not regressions, "Release blocked by sample regressions: " + "; ".join(regressions)
    assert (any(hits[f] > baseline["matches"][f] for f in SCORED_FIELDS)
            or error / len(samples) < Decimal(baseline["amount_diagnostics"]["mean_absolute_error_fraction_of_request"])), "Release requires a measured sample improvement"


@pytest.mark.parametrize(
    "request_id",
    ["request_01", "request_02", "request_03", "request_19"],
)
def test_key_sample_exact(engine, request_id):
    samples = {row[0].request_id: row for row in _load_sample_requests()}
    request, label = samples[request_id]
    result = engine.decide(request)
    assert result.affordability_status == label["affordability_status"]
    assert result.recommended_payment_method == label["recommended_payment_method"]
