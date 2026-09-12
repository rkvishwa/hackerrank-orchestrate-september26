#!/usr/bin/env python3
"""Evaluate predictions against sample_requests.csv and validate output contract."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from buy_or_wait.domain import OUTPUT_COLUMNS
from buy_or_wait.engine import DecisionEngine, run_pipeline
from buy_or_wait.config import Settings
from buy_or_wait.ingest.loader import load_dataset
from buy_or_wait.verification.verifier import OutputVerifier


def load_sample_labels(dataset_dir: Path) -> dict[str, dict[str, str]]:
    path = dataset_dir / "sample_requests.csv"
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["request_id"]: row for row in csv.DictReader(fh)}


def score_samples(dataset_dir: Path) -> dict[str, float]:
    settings = Settings(dataset_dir=dataset_dir, deterministic_mode=True, llm_enabled=False)
    dataset = load_dataset(dataset_dir)
    engine = DecisionEngine(dataset, settings)
    labels = load_sample_labels(dataset_dir)
    fields = [
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation",
    ]
    matches = {field: 0 for field in fields}
    total = 0
    for request_id, label in labels.items():
        request = dataset.requests_by_id.get(request_id)
        if request is None:
            sample_path = dataset_dir / "sample_requests.csv"
            with sample_path.open(encoding="utf-8-sig", newline="") as fh:
                for row in csv.DictReader(fh):
                    if row["request_id"] == request_id:
                        from buy_or_wait.ingest.loader import RequestRow
                        from datetime import date
                        from decimal import Decimal

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
                        break
        if request is None:
            continue
        result = engine.decide(request)
        total += 1
        for field in fields:
            predicted = getattr(result, field)
            if field == "amount_safe_to_pay":
                predicted = str(predicted)
            if str(predicted) == str(label[field]):
                matches[field] += 1
    return {field: (matches[field] / total if total else 0.0) for field in fields}


def validate_output(output_path: Path, dataset_dir: Path) -> list[str]:
    errors: list[str] = []
    with output_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        errors.extend(OutputVerifier.verify_csv_header(list(reader.fieldnames or [])))
        rows = list(reader)
    expected_ids = {row["request_id"] for row in csv.DictReader((dataset_dir / "requests.csv").open(encoding="utf-8-sig"))}
    seen = {row["request_id"] for row in rows}
    if seen != expected_ids:
        errors.append(f"request_id mismatch: expected {len(expected_ids)} got {len(seen)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", type=Path, default=Path("dataset"))
    parser.add_argument("--output", type=Path, default=Path("output.csv"))
    parser.add_argument("--score-samples", action="store_true")
    args = parser.parse_args()

    if args.score_samples:
        scores = score_samples(args.dataset_dir.resolve())
        for field, value in scores.items():
            print(f"{field}: {value:.1%}")
        return 0

    errors = validate_output(args.output.resolve(), args.dataset_dir.resolve())
    if errors:
        for err in errors:
            print(err)
        return 1
    print("Output validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
