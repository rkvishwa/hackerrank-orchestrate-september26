from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from buy_or_wait.config import Settings
from buy_or_wait.evidence.messages import MessageResolver
from buy_or_wait.ingest.loader import load_dataset

DATASET = Path(__file__).resolve().parents[2] / "dataset"


def test_salary_amendment_user_02():
    dataset = load_dataset(DATASET)
    resolver = MessageResolver(dataset, Settings(deterministic_mode=True, llm_enabled=False))
    ctx = resolver.resolve_for_user("user_02", date(2025, 8, 5), "request_02")
    assert ctx.income_patches
    assert any(p.amount == Decimal("42750000") for p in ctx.income_patches if p.amount)


def test_transfer_suppression_user_33():
    dataset = load_dataset(DATASET)
    resolver = MessageResolver(dataset, Settings(deterministic_mode=True, llm_enabled=False))
    ctx = resolver.resolve_for_user("user_33", date(2026, 1, 3), "request_33")
    assert ctx.notes
