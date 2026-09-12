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


@pytest.fixture(scope="module")
def engine():
    dataset = load_dataset(DATASET)
    return DecisionEngine(dataset, Settings(deterministic_mode=True, llm_enabled=False))


def _sample_rows():
    with (DATASET / "sample_requests.csv").open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def test_sample_status_is_valid_enum(engine):
    for row in _sample_rows():
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
        result = engine.decide(request)
        assert result.affordability_status in {
            "affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"
        }
        assert result.recommended_payment_method in {
            "full_payment", "partial_payment", "installments", "wait", "not_recommended"
        }
