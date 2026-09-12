from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from buy_or_wait.evidence.models import EvidenceContext
from buy_or_wait.ingest.loader import Dataset, FinancialEvent, Profile
from buy_or_wait.finance.recurrence import SPECULATIVE, series_identity, _apply_income_patches


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
        if patch.cancel or patch.suppress:
            values['status'] = 'cancelled'
    if event.event_id in evidence.suppressed_event_ids:
        values['status'] = 'cancelled'
    return replace(event, **values)


def resolve_user_events(dataset: Dataset, profile: Profile, user_id: str, request_date: date,
                        horizon_end: date, amount_overrides: dict[str, Decimal] | None = None,
                        evidence: EvidenceContext | None = None) -> list[ResolvedEvent]:
    from buy_or_wait.finance.currency import CurrencyConverter
    evidence = evidence or EvidenceContext()
    if amount_overrides:
        evidence = replace(evidence, amount_overrides={**evidence.amount_overrides, **amount_overrides})
    converter = CurrencyConverter(dataset.exchange_rates)
    resolved = []
    seen = set()
    for original in dataset.events_by_user.get(user_id, []):
        event = effective_event(original, evidence)
        if event.status in {'failed', 'cancelled', 'unrealized'} or event.direction == 'non_cash':
            continue
        if event.event_type == 'investment_valuation':
            continue
        if event.status == 'settled' and event.settlement_date < request_date:
            continue
        if event.settlement_date > horizon_end:
            continue
        if event.direction == 'credit':
            if event.status != 'settled' and not (
                event.status == 'scheduled' and event.category == 'salary'
                and not any(w in event.description.lower() for w in SPECULATIVE)
            ):
                continue
        elif event.direction != 'debit' or event.status not in {'settled', 'pending', 'scheduled'}:
            continue
        amount = event.amount
        if amount is None:
            raise ValueError(f'Unresolved required amount for {event.event_id}; extract or verify its image before running')
        if not amount.is_finite() or amount < 0:
            raise ValueError(f'Invalid monetary amount for {event.event_id}')
        if event.category == 'salary' and event.direction == 'credit' and event.status != 'settled':
            amount = _apply_income_patches(event, event.settlement_date, evidence)
            if amount is None:
                continue
        if event.category == 'rent':
            for patch in evidence.rent_patches:
                if event.settlement_date >= patch.effective_from:
                    amount = (amount * patch.multiplier).quantize(Decimal('0.01'))
        amount_home = converter.convert(amount, event.currency, profile.home_currency, event.settlement_date)
        # Past-due unsettled debits are still liabilities, reserved immediately.
        cash_date = max(request_date, event.settlement_date)
        key = (event.settlement_date, event.direction, event.category, event.currency,
               event.description, amount, event.status)
        if key in seen:
            continue
        seen.add(key)
        resolved.append(ResolvedEvent(event.event_id, event.category, event.direction, amount_home,
                       cash_date, event.status, event.flexibility, event.minimum_allowed_amount,
                       'event', True, series_key=series_identity(event)))
    return resolved
