from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from buy_or_wait.config import Settings
from buy_or_wait.domain import OUTPUT_COLUMNS
from buy_or_wait.engine import DecisionEngine, run_pipeline
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.verification.verifier import OutputVerifier


DATASET = Path(__file__).resolve().parents[2] / "dataset"


@pytest.fixture(scope="module")
def dataset():
    return load_dataset(DATASET)


@pytest.fixture(scope="module")
def engine(dataset):
    return DecisionEngine(dataset, Settings(deterministic_mode=True, llm_enabled=False))


def test_load_dataset(dataset):
    assert len(dataset.requests) == 250
    assert len(dataset.profiles) == 275


def test_output_columns():
    assert len(OUTPUT_COLUMNS) == 8


def test_single_decision_bounds(engine, dataset):
    request = dataset.requests[0]
    result = engine.decide(request)
    assert Decimal("0") <= result.amount_safe_to_pay <= request.requested_amount


def test_batch_writes_output(tmp_path):
    settings = Settings(
        dataset_dir=DATASET,
        output_path=tmp_path / "output.csv",
        deterministic_mode=True,
        llm_enabled=False,
    )
    results, path = run_pipeline(settings)
    assert len(results) == 250
    assert path.exists()
    with path.open(encoding="utf-8") as fh:
        header = fh.readline().strip().split(",")
    assert header == OUTPUT_COLUMNS


def test_verifier_rejects_bad_amount(engine, dataset):
    request = dataset.requests[0]
    result = engine.decide(request)
    result.amount_safe_to_pay = request.requested_amount + Decimal("1")
    errors = OutputVerifier.verify_request_row(request, result)
    assert errors
