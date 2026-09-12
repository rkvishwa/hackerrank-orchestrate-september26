from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from buy_or_wait.domain import DecisionResult, PaymentLeg
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


def forecast_audit(engine, request, context):
    """Explain capacity from input evidence only; reference labels never affect it."""
    profile = engine.dataset.profiles[request.user_id]
    balance = profile.current_available_balance
    minimum = balance
    binding = {"date": request.request_date.isoformat(), "source": "opening_balance"}
    ledger = []
    for flow in sorted(engine.forecast.build_cashflows(profile, request, evidence=context),
                       key=lambda f: (f.flow_date, f.direction != "credit", f.source)):
        balance += flow.amount if flow.direction == "credit" else -flow.amount
        row = {"date": flow.flow_date.isoformat(), "direction": flow.direction, "amount": str(flow.amount),
               "category": flow.category, "source": flow.source, "balance_after": str(balance),
               "headroom_after": str(balance - profile.minimum_balance_to_keep)}
        ledger.append(row)
        if balance < minimum:
            minimum, binding = balance, row
    estimates = []
    from buy_or_wait.finance.recurrence import series_identity
    from buy_or_wait.finance.events import effective_event
    history = [effective_event(e, context) for e in engine.dataset.events_by_user[request.user_id]
               if e.status == "settled" and e.settlement_date < request.request_date]
    for series in engine.forecast._series_for_user(request.user_id, request.request_date, context):
        values = [e.amount for e in history if series_identity(e) == series.series_key and e.amount is not None]
        estimates.append({"source": f"series:{series.template_event_id}", "identity": series.series_key,
            "amount": str(series.amount), "currency": series.currency, "cadence_days": series.cadence_days,
            "monthly": series.monthly, "history_count": len(values),
            "history_min": str(min(values)) if values else None,
            "history_max": str(max(values)) if values else None,
            "history_mean": str(sum(values) / len(values)) if values else None,
            "amount_varies_in_history": len(set(values)) > 1})
    return {"opening_balance": str(profile.current_available_balance), "minimum_balance": str(minimum),
            "headroom_at_minimum": str(minimum - profile.minimum_balance_to_keep),
            "baseline_shortfall": minimum < profile.minimum_balance_to_keep,
            "binding_cashflow": binding, "ledger": ledger, "recurring_estimates": estimates,
            "image_amounts": {eid: str(amount) for eid, amount in context.amount_overrides.items()}}


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
    comparisons = []
    amount_errors = []
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
            delta = result.amount_safe_to_pay - Decimal(row["amount_safe_to_pay"])
            amount_errors.append(abs(delta) / request.requested_amount)
            comparisons.append({"request_id": request.request_id,
                "fields": {field: {"predicted": str(getattr(result, field)), "sample": row[field],
                          "matches": field not in mismatch} for field in SCORED_FIELDS},
                "amount_difference": str(delta), "absolute_error_fraction_of_request": str(amount_errors[-1])})
            if mismatch:
                context = engine.evidence.resolve(request)
                profile = engine.dataset.profiles[request.user_id]
                baseline = engine.forecast.simulate_plan(profile, request, [], evidence=context)
                sample_plan = engine.forecast.simulate_plan(profile, request, parse_plan(row["payment_plan"]),
                                                            parse_spending(row["spending_changes_needed"]), evidence=context)
                audit = forecast_audit(engine, request, context)
                sample_amount_replay = engine.forecast.simulate_plan(profile, request,
                    [PaymentLeg(request.request_date, Decimal(row["amount_safe_to_pay"]))], evidence=context)
                investigation = [f"Capacity is limited on {audit['binding_cashflow']['date']} by "
                                 f"{audit['binding_cashflow']['source']}."]
                if audit["baseline_shortfall"]:
                    investigation.append("The baseline falls below the reserve even without a purchase; positive payment capacity is unsafe under this forecast.")
                if any(s["amount_varies_in_history"] for s in audit["recurring_estimates"]):
                    investigation.append("Variable historical amounts require estimates; inspect recurring_estimates and the ledger for their effect.")
                investigation.append("The public example supplies a final answer, not its underlying forecast. Residual differences cannot be attributed to a specific reference transaction without that forecast.")
                differences.append({"request_id": request.request_id, "fields": mismatch,
                    "baseline_minimum": str(baseline.min_balance), "required_minimum": str(profile.minimum_balance_to_keep),
                    "sample_plan_safe_under_this_forecast": sample_plan.safe,
                    "sample_plan_minimum_under_this_forecast": str(sample_plan.min_balance),
                    "evidence_notes": context.notes,
                    "investigation": " ".join(investigation), "forecast_audit": audit,
                    "sample_amount_safe_under_this_forecast": sample_amount_replay.safe,
                    "forecast": [{"date": c.flow_date.isoformat(), "direction": c.direction,
                                  "amount": str(c.amount), "category": c.category, "source": c.source}
                                 for c in sorted(engine.forecast.build_cashflows(profile, request, evidence=context),
                                                 key=lambda c: (c.flow_date, c.direction, c.source))]})
    return {"available": True, "request_count": total, "matches": matches,
            "accuracy": {k: v / total if total else 0 for k, v in matches.items()},
            "differences": differences, "comparisons": comparisons,
            "amount_diagnostics": {"mean_absolute_error_fraction_of_request": str(sum(amount_errors) / total) if total else None,
                "overestimates": sum(Decimal(c["amount_difference"]) > 0 for c in comparisons),
                "underestimates": sum(Decimal(c["amount_difference"]) < 0 for c in comparisons),
                "exact_matches": matches["amount_safe_to_pay"],
                "note": "Supplementary error magnitude, not a replacement for exact matches or the unknown official scoring formula."},
            "hidden_dataset_accuracy": "unknown"}
