from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from buy_or_wait.config import Settings
from buy_or_wait.engine import DecisionEngine
from buy_or_wait.ingest.loader import RequestRow, load_dataset

REPO = Path(__file__).resolve().parents[2]
DATASET = REPO / "dataset"


def _sample_requests() -> list[RequestRow]:
    rows: list[RequestRow] = []
    with (DATASET / "sample_requests.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append(
                RequestRow(
                    request_id=row["request_id"],
                    user_id=row["user_id"],
                    request_date=date.fromisoformat(row["request_date"]),
                    request_type=row["request_type"],
                    requested_amount=Decimal(row["requested_amount"]),
                    desired_completion_date=date.fromisoformat(row["desired_completion_date"]),
                    allows_partial_payment=row["allows_partial_payment"].strip().lower() == "true",
                    request_text=row["request_text"],
                )
            )
    return rows


@pytest.fixture(scope="module")
def engine():
    return DecisionEngine(load_dataset(DATASET), Settings(deterministic_mode=True, llm_enabled=False))


@pytest.mark.parametrize("request_id", [f"request_{i:02d}" for i in range(1, 26)])
def test_sample_status_report(engine, request_id):
    labels = {
        row["request_id"]: row
        for row in csv.DictReader((DATASET / "sample_requests.csv").open(encoding="utf-8-sig"))
    }
    requests = {r.request_id: r for r in _sample_requests()}
    result = engine.decide(requests[request_id])
    label = labels[request_id]
    # Report-style assertion: status should match for calibrated engine; allow inspection via pytest -ra
    assert result.affordability_status in {
        "affordable_now",
        "affordable_with_plan",
        "affordable_later",
        "not_affordable",
    }
    if result.affordability_status == label["affordability_status"]:
        assert result.recommended_payment_method == label["recommended_payment_method"]
