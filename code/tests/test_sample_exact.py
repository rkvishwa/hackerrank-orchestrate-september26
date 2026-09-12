from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import RequestRow, load_dataset

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


def test_sample_regression_thresholds(engine):
    samples = _load_sample_requests()
    status_hits = 0
    method_hits = 0
    for request, label in samples:
        result = engine.decide(request)
        if result.affordability_status == label["affordability_status"]:
            status_hits += 1
        if result.recommended_payment_method == label["recommended_payment_method"]:
            method_hits += 1
    total = len(samples)
    assert status_hits / total >= 0.70, f"status match {status_hits}/{total}"
    assert method_hits / total >= 0.80, f"method match {method_hits}/{total}"


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
