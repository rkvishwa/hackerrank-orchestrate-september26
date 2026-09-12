from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from buy_or_wait.domain import DecisionResult
from buy_or_wait.ingest.loader import RequestRow
from buy_or_wait.verification.verifier import OutputVerifier, parse_plan, parse_spending

SCORED_FIELDS = ("amount_safe_to_pay", "affordability_status", "recommended_payment_method",
                 "payment_plan", "earliest_date_for_full_payment", "spending_changes_needed")


def normalize(field, value):
    if field == "amount_safe_to_pay":
        return Decimal(str(value))
    if field == "payment_plan":
        return parse_plan(value)
    if field == "spending_changes_needed":
        return sorted((c.action, c.event_id, c.new_amount) for c in parse_spending(value))
    return str(value)


def validate_output(output_path: Path, engine, expected_ids=None):
    errors = []
    with output_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        errors.extend(OutputVerifier.verify_csv_header(list(reader.fieldnames or [])))
        rows = list(reader)
    if errors:
        return errors
    expected = set(expected_ids if expected_ids is not None else engine.dataset.requests_by_id)
    counts = Counter(row.get("request_id") for row in rows)
    if set(counts) != expected:
        errors.append(f"request IDs differ: missing={sorted(expected - set(counts))}; unknown={sorted(set(counts) - expected)}")
    duplicates = sorted(k for k, n in counts.items() if n != 1)
    if duplicates:
        errors.append(f"duplicate request IDs: {duplicates}")
    for row in rows:
        rid = row.get("request_id")
        if rid not in engine.dataset.requests_by_id:
            continue
        try:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("incorrect CSV field count")
            result = DecisionResult(**{**row, "amount_safe_to_pay": Decimal(row["amount_safe_to_pay"])})
            request = engine.dataset.requests_by_id[rid]
            context = engine.evidence.resolve(request)
            row_errors = engine.verifier.verify_request_row(
                request, result, engine.dataset.profiles[request.user_id],
                engine.dataset.payment_options_by_request.get(rid, []), evidence=context)
            errors.extend(f"{rid}: {error}" for error in row_errors)
        except (ValueError, InvalidOperation, TypeError, KeyError) as exc:
            errors.append(f"{rid}: malformed or unresolved row: {exc}")
    return errors


def score_samples(dataset_dir: Path, settings):
    # Samples are evaluated separately; labels never enter the prediction pipeline.
    from buy_or_wait.engine import DecisionEngine
    from buy_or_wait.ingest.loader import load_dataset
    from buy_or_wait.llm.usage import UsageTracker
    sample_path = dataset_dir / "sample_requests.csv"
    if not sample_path.exists():
        return {"available": False, "hidden_dataset_accuracy": "unknown"}
    engine = DecisionEngine(load_dataset(dataset_dir), settings)
    matches = {field: 0 for field in SCORED_FIELDS}
    differences = []
    total = 0
    with sample_path.open(encoding="utf-8-sig", newline="") as fh, UsageTracker.scoped(settings.model_prices):
        for row in csv.DictReader(fh):
            request = RequestRow(row["request_id"], row["user_id"], date.fromisoformat(row["request_date"]),
                row["request_type"], Decimal(row["requested_amount"]), date.fromisoformat(row["desired_completion_date"]),
                row["allows_partial_payment"].lower() == "true", row["request_text"])
            result = engine.decide(request)
            total += 1
            mismatch = {}
            for field in SCORED_FIELDS:
                predicted = getattr(result, field)
                if normalize(field, predicted) == normalize(field, row[field]):
                    matches[field] += 1
                else:
                    mismatch[field] = {"predicted": str(predicted), "sample": row[field]}
            if mismatch:
                context = engine.evidence.resolve(request)
                profile = engine.dataset.profiles[request.user_id]
                baseline = engine.forecast.simulate_plan(profile, request, [], evidence=context)
                sample_plan = engine.forecast.simulate_plan(profile, request, parse_plan(row["payment_plan"]),
                                                            parse_spending(row["spending_changes_needed"]), evidence=context)
                differences.append({"request_id": request.request_id, "fields": mismatch,
                    "baseline_minimum": str(baseline.min_balance), "required_minimum": str(profile.minimum_balance_to_keep),
                    "sample_plan_safe_under_this_forecast": sample_plan.safe,
                    "sample_plan_minimum_under_this_forecast": str(sample_plan.min_balance),
                    "evidence_notes": context.notes,
                    "investigation": "Compare the conservative forecast and evidence below with the supplied example; no hidden labels are available.",
                    "forecast": [{"date": c.flow_date.isoformat(), "direction": c.direction,
                                  "amount": str(c.amount), "category": c.category, "source": c.source}
                                 for c in sorted(engine.forecast.build_cashflows(profile, request, evidence=context),
                                                 key=lambda c: (c.flow_date, c.direction, c.source))]})
    return {"available": True, "request_count": total, "matches": matches,
            "accuracy": {k: v / total if total else 0 for k, v in matches.items()},
            "differences": differences, "hidden_dataset_accuracy": "unknown"}
