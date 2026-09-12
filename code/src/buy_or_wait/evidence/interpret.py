"""Deterministic application of quoted semantic facts to one person's records."""
from datetime import date, timedelta
from decimal import Decimal
import re

from buy_or_wait.evidence.models import EvidenceContext, EventPatch, IncomeSchedulePatch, RentPatch
from buy_or_wait.finance.recurrence import detect_recurring_series, project_series_dates, series_identity, SPECULATIVE
from buy_or_wait.finance.income import (associate_income, income_target_key,
                                       select_income_targets, income_scope_event_ids)


def interpret_message(dataset, settings, message, as_of, payload):
    ctx = EvidenceContext()
    events = dataset.events_by_user.get(message.user_id, [])
    linked = dataset.events_by_id.get(message.related_event_id)
    if linked and linked.user_id != message.user_id:
        raise ValueError("Cross-user evidence target")
    incomes = [e for e in events if e.direction == "credit" and e.category == "salary"
               and not any(w in e.description.lower() for w in SPECULATIVE)]
    series = detect_recurring_series(incomes, as_of, settings.recurrence)
    keys = {s.series_key for s in series} or {series_identity(e) for e in incomes if e.settlement_date < as_of}
    associations = associate_income(events, as_of)

    def targets(fact):
        return select_income_targets(incomes, associations, keys,
            linked_event_id=message.related_event_id, currency=fact["currency"],
            subject=fact.get("subject") or "", quote=fact["quote"])

    def next_cycle(selected):
        dates = [e.settlement_date for e in incomes if e.status == "scheduled" and e.settlement_date >= as_of
                 and income_target_key(e, associations) in selected]
        for s in series:
            if s.series_key in selected:
                anchor = dataset.events_by_id[s.template_event_id].settlement_date
                dates.extend(project_series_dates(as_of, as_of + timedelta(days=45), s.cadence_days,
                    anchor, monthly=s.monthly, anchor_day=s.anchor_day))
        return min(dates) if dates else None

    def add_income(patch, selected):
        patch.ambiguous_target = len(selected) != 1
        patch.target_series_keys = tuple(sorted(selected)) if not patch.ambiguous_target else ()
        patch.target_event_ids = income_scope_event_ids(incomes, associations, selected,
                                                       linked_event_id=message.related_event_id)
        ctx.income_patches.append(patch)

    for fact in payload.get("accepted", []):
        kind = fact["kind"]
        amount = Decimal(fact["amount"]) if fact["amount"] is not None else None
        effective = date.fromisoformat(fact["effective_date"]) if fact["effective_date"] else None
        selected = targets(fact)
        reason = "informational; no additional cash"
        if (kind == "income_end" and not linked and any(f["kind"] == "household_income_remaining"
                and f["certainty"] == "confirmed" for f in payload.get("accepted", []))):
            # These are two clauses of one amendment, not an instruction to end
            # the very salary the message explicitly says remains confirmed.
            ctx.fact_audit.append({"source_id": message.message_id, "user_id": message.user_id,
                "observed_at": message.sent_at, "fact": fact,
                "resolution": "termination is handled by household survivor resolution"})
            continue
        if kind in {"income_amount", "income_resume", "income_end", "income_date", "household_income_remaining"}:
            if fact["certainty"] != "confirmed":
                reason = "income is not confirmed"
            elif kind == "household_income_remaining" and amount is not None:
                # If only one historical stream is still active, it is identifiable even
                # when its new confirmed salary differs from the old amount.
                survivors = {s.series_key for s in series if s.series_key in selected}
                matching = {s.series_key for s in series if s.series_key in selected and s.amount == amount}
                survivors = matching or survivors
                if len(survivors) == 1:
                    all_keys = {series_identity(e) for e in incomes}
                    for key in all_keys - survivors:
                        add_income(IncomeSchedulePatch(stop_after=effective or as_of), {key})
                    add_income(IncomeSchedulePatch(amount=amount, currency=fact["currency"],
                        effective_from=effective or as_of), survivors)
                    reason = "remaining identifiable salary amended; ended streams excluded"
                else:
                    reason = "ambiguous household survivor; no salary increase applied"
            elif selected:
                cycle = next_cycle(selected)
                patch = IncomeSchedulePatch(currency=fact["currency"])
                if kind == "income_end":
                    patch.stop_after = effective or as_of
                elif kind == "income_date":
                    patch.original_date, patch.payment_date = cycle, effective
                else:
                    patch.amount = amount
                    patch.effective_from = effective or (cycle if fact["timing"] == "next_occurrence" else as_of)
                    if fact["scope"] == "occurrence":
                        patch.effective_until = effective or cycle
                    if kind == "income_resume":
                        patch.resume_from = effective
                add_income(patch, selected)
                reason = "scoped income amendment" if len(selected) == 1 else "ambiguous income target; no increase or resumption"
            elif amount is not None and effective and kind in {"income_amount", "income_resume"}:
                existing = [e for e in incomes if e.status == "scheduled" and e.settlement_date == effective
                            and e.currency == fact["currency"]]
                if len(existing) == 1:
                    ctx.event_patches[existing[0].event_id] = EventPatch(existing[0].event_id, amount=amount)
                elif not existing and (not incomes or re.search(r"\bfirst (?:salary|payroll)\b", fact["quote"], re.I)):
                    ctx.confirmed_flows.append({"date": effective, "amount": amount, "currency": fact["currency"],
                        "direction": "credit", "category": "salary", "source": message.message_id})
                reason = ("explicit dated first salary; no unsupported later recurrence" if existing or ctx.confirmed_flows
                          else "unmatched employment amendment; no additional income invented")
            else:
                reason = "income target/date unresolved; no invented income"
        elif kind == "pending_credit":
            if any(term in (fact["quote"] + " " + (fact.get("subject") or "")).lower()
                   for term in ("platform", "payout", "earnings", "aplikasi", "saldo", "withdraw")):
                add_income(IncomeSchedulePatch(unconfirmed_variable_income=True), selected)
            reason = "unsettled credit excluded"
        elif kind in {"settlement", "cancellation", "retry_debit"} and linked:
            if kind == "settlement" and fact["certainty"] == "confirmed":
                ctx.event_patches[linked.event_id] = EventPatch(linked.event_id, amount=amount,
                    status="settled", settlement_date=effective)
                reason = "settlement applied using documented date or existing event date"
            elif kind == "cancellation" and fact["certainty"] == "confirmed":
                ctx.event_patches[linked.event_id] = EventPatch(linked.event_id, cancel=True,
                    cancel_scope="series" if fact["scope"] == "series" else "occurrence",
                    cancel_from=effective or as_of if fact["scope"] == "series" else None)
                reason = "cancellation scoped to " + fact["scope"]
            elif kind == "retry_debit":
                reason = "failed attempt has no cash effect; retain supplied outstanding retry"
        elif kind == "expense_percent" and fact["percentage"] is not None:
            subject = (fact.get("subject") or fact["quote"]).lower()
            if "rent" in subject or "sewa" in subject or "lease" in subject:
                multiplier = 1 + Decimal(fact["percentage"]) / 100
                rent_keys = {s.series_key for s in detect_recurring_series(events, as_of, settings.recurrence)
                             if s.category == "rent" and s.direction == "debit"}
                identified = {series_identity(linked)} & rent_keys if linked else set()
                named = {series_identity(e) for e in events if e.category == "rent"
                         and e.description.lower() in fact["quote"].lower()}
                selected_rent = identified or (named & rent_keys) or rent_keys
                if len(selected_rent) == 1:
                    ctx.rent_patches.append(RentPatch(multiplier, effective or as_of, tuple(selected_rent)))
                    reason = "identified rent recurrence amended; issued balances due unchanged"
                else:
                    ctx.unresolved_mandatory_debits.add(message.message_id)
                    reason = "rent amendment target unresolved; cannot certify positive capacity"
        elif kind == "expense_start":
            words = set(re.findall(r"[a-z]+", (fact.get("subject") or fact["quote"]).lower()))
            words -= {"a", "the", "new", "recurring", "payment", "starts", "begins", "in", "same", "month"}
            matches = [e for e in events if e.direction == "debit" and words & set(re.findall(r"[a-z]+", e.description.lower()))]
            if matches:
                reason = "commitment already represented by supplied financial events"
            elif amount is not None and effective and fact["currency"]:
                ctx.confirmed_flows.append({"date": effective, "amount": amount, "currency": fact["currency"],
                    "direction": "debit", "category": "essential", "source": message.message_id})
                reason = "explicit first commitment; future cadence requires evidence"
            else:
                ctx.unresolved_mandatory_debits.add(message.message_id)
                reason = "new mandatory commitment lacks amount/date; positive capacity cannot be certified"
        elif kind == "internal_transfer":
            pairs = []
            for debit in events:
                if debit.direction != "debit" or debit.amount is None:
                    continue
                for credit in events:
                    if (credit.direction == "credit" and credit.amount == debit.amount
                            and credit.currency == debit.currency and credit.settlement_date == debit.settlement_date
                            and (not linked or linked.event_id in {debit.event_id, credit.event_id})):
                        pairs.append((debit, credit))
            if len(pairs) == 1:
                ctx.suppressed_event_ids.update(e.event_id for e in pairs[0])
                reason = "uniquely matched same-owner internal transfer; net zero"
            else:
                reason = "internal transfer pair ambiguous; no unrelated records suppressed"
        elif kind in {"reimbursement", "one_time_income"}:
            if linked:
                ctx.nonrecurring_event_ids.add(linked.event_id)
            reason = "one-time income is not recurring salary; retain actual settled cash state"
        elif kind == "expense_amount" and amount is not None and linked and linked.direction == "debit":
            ctx.event_patches[linked.event_id] = EventPatch(linked.event_id, amount=amount, settlement_date=effective)
            reason = "linked expense amendment"
        ctx.fact_audit.append({"source_id": message.message_id, "user_id": message.user_id,
            "observed_at": message.sent_at, "fact": fact, "resolution": reason,
            "income_candidate_series": sorted(selected) if kind.startswith("income_") or kind == "household_income_remaining" else [],
            "income_target_ambiguous": len(selected) > 1 if kind.startswith("income_") else False})
        ctx.notes.append(f"{message.message_id}: {reason}")
    for rejected in payload.get("rejected", []):
        ctx.fact_audit.append({"source_id": message.message_id, "user_id": message.user_id,
            "rejected": rejected})
    return ctx
