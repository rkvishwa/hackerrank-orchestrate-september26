from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from buy_or_wait.evidence.models import EvidenceContext
from buy_or_wait.ingest.loader import Dataset, FinancialEvent, Profile
from buy_or_wait.finance.recurrence import SPECULATIVE, series_identity, _apply_income_patches, income_payment_date


@dataclass
class ResolvedEvent:
    event_id: str
    category: str
    direction: str
    amount_home: Decimal
    settlement_date: date
    status: str
    flexibility: str
    minimum_allowed_amount: Decimal | None
    source: str
    include_in_forecast: bool
    stopped: bool = False
    reduced_to: Decimal | None = None
    series_key: str | None = None


def effective_event(event: FinancialEvent, evidence: EvidenceContext) -> FinancialEvent:
    patch = evidence.event_patches.get(event.event_id)
    values = {}
    if event.event_id in evidence.amount_overrides:
        values['amount'] = evidence.amount_overrides[event.event_id]
    if patch:
        for name in ('amount', 'currency', 'settlement_date', 'status'):
            if getattr(patch, name) is not None:
                values[name] = getattr(patch, name)
        if patch.suppress or (patch.cancel and (patch.cancel_scope == 'occurrence'
                or patch.cancel_from is None or event.settlement_date >= patch.cancel_from)):
            values['status'] = 'cancelled'
    if event.event_id in evidence.suppressed_event_ids:
        values['status'] = 'cancelled'
    result = replace(event, **values)
    if result.status != 'settled':
        result = replace(result, settlement_date=income_payment_date(result, result.settlement_date, evidence))
    return result


def resolve_user_events(dataset: Dataset, profile: Profile, user_id: str, request_date: date,
                        horizon_end: date, amount_overrides: dict[str, Decimal] | None = None,
                        evidence: EvidenceContext | None = None,
                        audit: list[dict] | None = None) -> list[ResolvedEvent]:
    from buy_or_wait.finance.currency import CurrencyConverter
    evidence = evidence or EvidenceContext()
    if amount_overrides:
        evidence = replace(evidence, amount_overrides={**evidence.amount_overrides, **amount_overrides})
    converter = CurrencyConverter(dataset.exchange_rates)
    resolved = []
    seen = {}
    for original in sorted(dataset.events_by_user.get(user_id, []), key=lambda e: (e.settlement_date, e.event_id)):
        event = effective_event(original, evidence)
        def record(reason, **details):
            if audit is not None:
                patch = evidence.event_patches.get(event.event_id)
                audit.append({"event_id": event.event_id, "reason": reason,
                              "supporting_records": [event.event_id] + ([patch.source] if patch and patch.source else []),
                              **details})
        if event.status in {'failed', 'cancelled', 'unrealized'} or event.direction == 'non_cash':
            record("non_cash" if event.direction == 'non_cash' else "effective_status_" + event.status)
            continue
        if event.event_type == 'investment_valuation':
            record("unrealized_investment_valuation")
            continue
        if event.status == 'settled' and event.settlement_date < request_date:
            record("historical_settlement_already_in_opening_balance")
            continue
        if event.settlement_date > horizon_end:
            record("settlement_outside_forecast", effective_date=str(event.settlement_date))
            continue
        if event.direction == 'credit':
            if event.status != 'settled' and not (
                event.status == 'scheduled' and event.category == 'salary'
                and not any(w in event.description.lower() for w in SPECULATIVE)
            ):
                record("unsettled_or_speculative_credit")
                continue
        elif event.direction != 'debit' or event.status not in {'settled', 'pending', 'scheduled'}:
            record("cash_state_not_payable")
            continue
        amount = event.amount
        if amount is None:
            raise ValueError(f'Unresolved required amount for {event.event_id}; extract or verify its image before running')
        if not amount.is_finite() or amount < 0:
            raise ValueError(f'Invalid monetary amount for {event.event_id}')
        if event.category == 'salary' and event.direction == 'credit' and event.status != 'settled':
            amount = _apply_income_patches(event, event.settlement_date, evidence)
            if amount is None:
                record("income_excluded_by_scoped_amendment")
                continue
        documented_amount = original.event_id in evidence.amount_overrides or (
            original.event_id in evidence.event_patches and
            evidence.event_patches[original.event_id].amount is not None)
        # A stated balance due is already the final liability. A generic lease
        # increase changes recurring rent, not an issued invoice or arrears.
        if event.category == 'rent' and not documented_amount and not any(
                word in event.description.lower() for word in ('outstanding', 'arrears', 'balance due')):
            for patch in evidence.rent_patches:
                if (event.settlement_date >= patch.effective_from and
                        (patch.target_series_keys is None or series_identity(event) in patch.target_series_keys)):
                    amount = (amount * patch.multiplier).quantize(Decimal('0.01'))
        amount_home = converter.convert(amount, event.currency, profile.home_currency, event.settlement_date)
        # Past-due unsettled debits are still liabilities, reserved immediately.
        cash_date = max(request_date, event.settlement_date)
        key = (event.settlement_date, event.direction, event.category, event.currency,
               event.description, amount, event.status)
        if key in seen:
            record("duplicate_cash_record", duplicate_of=seen[key])
            continue
        seen[key] = event.event_id
        resolved.append(ResolvedEvent(event.event_id, event.category, event.direction, amount_home,
                       cash_date, event.status, event.flexibility, event.minimum_allowed_amount,
                       'event', True, series_key=series_identity(event)))
        record("explicit_projected_cash_flow", cash_date=str(cash_date), amount_home=str(amount_home),
               exchange_rate_date=str(event.settlement_date))
    return resolved
