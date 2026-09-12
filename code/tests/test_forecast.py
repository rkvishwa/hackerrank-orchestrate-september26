from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.domain import PaymentLeg
from buy_or_wait.finance.forecast import ForecastEngine
from buy_or_wait.ingest.loader import load_dataset


DATASET = Path(__file__).resolve().parents[2] / "dataset"


def test_max_safe_payment_non_negative():
    dataset = load_dataset(DATASET)
    engine = ForecastEngine(dataset, Settings())
    request = dataset.requests[0]
    profile = dataset.profiles[request.user_id]
    safe = engine.max_safe_payment(profile, request)
    assert safe >= Decimal("0")


def test_simulation_respects_minimum():
    dataset = load_dataset(DATASET)
    engine = ForecastEngine(dataset, Settings())
    request = dataset.requests[0]
    profile = dataset.profiles[request.user_id]
    huge = PaymentLeg(payment_date=request.request_date, amount=request.requested_amount * 100)
    result = engine.simulate_plan(profile, request, [huge])
    assert result.safe is False
