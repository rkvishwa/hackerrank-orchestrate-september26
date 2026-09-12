"""Record accounting coverage separately from the numerical capacity oracle."""
from dataclasses import asdict
from collections import Counter
from datetime import timedelta
from decimal import Decimal

from buy_or_wait.finance.events import effective_event, resolve_user_events
from buy_or_wait.plans.enumerator import _installment_legs, _months_span


def case_audit(engine, request, evidence, candidates, selected):
    from buy_or_wait.artifacts.evaluation import forecast_audit
    dataset = engine.dataset
    profile = dataset.profiles[request.user_id]
    baseline = forecast_audit(engine, request, evidence)
    series = engine.forecast._series_for_user(request.user_id, request.request_date, evidence)
    members = {}
    for item in series:
        for eid in item.member_event_ids:
            if eid in members:
                raise ValueError(f"Recurring source belongs to multiple series: {eid}")
            members[eid] = item.series_key
        if set(item.cancellation_event_ids) & set(item.member_event_ids):
            raise ValueError("Cancelled calendar evidence cannot be an amount observation")
    cashflows = engine.forecast.build_cashflows(profile, request, evidence=evidence)
    projected = Counter(f.source for f in cashflows)
    history = []
    horizon = request.request_date + timedelta(days=engine.settings.forecast_horizon_days - 1)
    resolutions = []
    explicit = resolve_user_events(dataset, profile, request.user_id, request.request_date, horizon,
                                   evidence=evidence, audit=resolutions)
    resolution_by_id = {r["event_id"]: r for r in resolutions}
    required_explicit = set()
    for event in explicit:
        if engine.forecast._cancelled_commitment(request.user_id, event.series_key, event.settlement_date, evidence):
            resolution_by_id[event.event_id]["reason"] = "ongoing_commitment_cancelled"
            continue
        required_explicit.add(event.event_id)
    for raw in dataset.events_by_user.get(request.user_id, []):
        expected = int(raw.event_id in required_explicit)
        if projected[raw.event_id] != expected:
            raise ValueError(f"Explicit cash accounting mismatch for {raw.event_id}: expected {expected}, got {projected[raw.event_id]}")
    for raw in sorted(dataset.events_by_user.get(request.user_id, []), key=lambda e: (e.settlement_date, e.event_id)):
        event = effective_event(raw, evidence)
        resolution = resolution_by_id[event.event_id]
        disposition = resolution["reason"]
        history.append({"original": asdict(raw), "effective": asdict(event), "disposition": disposition,
                        "cash_resolution": resolution, "recurring_series": members.get(event.event_id),
                        "cancellation_calendar_for": [s.series_key for s in series if event.event_id in s.cancellation_event_ids]})
    source_ids = [row["original"]["event_id"] for row in history]
    if len(source_ids) != len(set(source_ids)) or set(source_ids) != {
            e.event_id for e in dataset.events_by_user.get(request.user_id, [])}:
        raise ValueError("Case accounting omitted or duplicated a source record")
    offers = []
    for option in dataset.payment_options_by_request.get(request.request_id, []):
        reasons = []
        if option.payment_method not in profile.payment_methods_user_will_consider:
            reasons.append("user does not accept method")
        legs = _installment_legs(option)
        if option.payment_method == "installments":
            if profile.max_installment_months is None or _months_span(request.request_date, option) > profile.max_installment_months:
                reasons.append("installment duration not permitted")
            if sum((p.amount for p in legs), Decimal("0")) != option.total_payable_amount:
                reasons.append("schedule total differs from supplied total")
        if legs and (legs[-1].payment_date > request.desired_completion_date or legs[0].payment_date < request.request_date):
            reasons.append("schedule outside request/deadline")
        offers.append({"option": asdict(option), "eligibility_rejections": reasons})
    plans = []
    for candidate in candidates:
        reasons = []
        if not candidate.safe:
            reasons.append("reserve breach or unquantified mandatory commitment")
        if not candidate.completes_by_deadline:
            reasons.append("misses completion deadline")
        if candidate.safe and candidate.completes_by_deadline and candidate != selected:
            reasons.append("ranked below selected plan by contract priorities")
        plans.append({"candidate": asdict(candidate), "selected": candidate == selected, "rejections": reasons})
    # Independently replay the chosen schedule against the adjusted cash ledger.
    cash = engine.forecast.build_cashflows(profile, request, spending_changes=selected.spending_changes, evidence=evidence)
    entries = [(f.flow_date, 0 if f.direction == "credit" else 1, f.source,
                f.amount if f.direction == "credit" else -f.amount) for f in cash]
    entries += [(p.payment_date, 2, "request_payment", -p.amount) for p in selected.legs]
    balance = profile.current_available_balance
    replay = []
    for day, _, source, delta in sorted(entries):
        balance += delta
        replay.append({"date": day, "source": source, "delta": delta, "balance": balance,
                       "headroom": balance - profile.minimum_balance_to_keep})
    if selected.legs and any(row["headroom"] < 0 for row in replay):
        raise ValueError("Independent plan replay breached reserve")
    return {"request": asdict(request), "profile": asdict(profile), "history": history,
        "accounting_coverage": {"source_records": len(history), "accounted_records": len(source_ids),
            "required_explicit_records": len(required_explicit), "explicit_records_verified_once": len(required_explicit),
            "unique_recurring_members": len(members),
            "unquantified_commitments": sorted(evidence.unresolved_mandatory_debits)},
        "evidence": evidence.fact_audit, "baseline": baseline, "offers": offers,
        "candidates": plans, "selected_plan_replay": replay}
