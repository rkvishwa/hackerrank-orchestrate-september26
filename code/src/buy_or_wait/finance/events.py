from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal

from buy_or_wait.ingest.loader import Dataset, FinancialEvent, Profile


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


def _should_exclude(event: FinancialEvent) -> bool:
    if event.status in {"failed", "cancelled"}:
        return True
    if event.status == "unrealized" or event.event_type == "investment_valuation":
        return True
    if event.direction == "non_cash":
        return True
    return False


def _include_credit(event: FinancialEvent) -> bool:
    if event.direction != "credit":
        return False
    if event.status == "settled":
        return True
    if event.status == "scheduled" and event.event_type == "income":
        return True
    return False


def _include_debit(event: FinancialEvent) -> bool:
    if event.direction != "debit":
        return False
    if event.status in {"pending", "scheduled", "settled"}:
        return True
    return False


def resolve_user_events(
    dataset: Dataset,
    profile: Profile,
    user_id: str,
    request_date: date,
    horizon_end: date,
    amount_overrides: dict[str, Decimal] | None = None,
) -> list[ResolvedEvent]:
    from buy_or_wait.finance.currency import CurrencyConverter

    converter = CurrencyConverter(dataset.exchange_rates)
    overrides = amount_overrides or {}
    cancelled_ids: set[str] = set()
    for event in dataset.events_by_user.get(user_id, []):
        if event.status == "cancelled":
            cancelled_ids.add(event.event_id)
            if event.linked_event_id:
                cancelled_ids.add(event.linked_event_id)

    resolved: list[ResolvedEvent] = []
    seen_keys: set[tuple[str, date, str, Decimal | None]] = set()

    for event in dataset.events_by_user.get(user_id, []):
        if _should_exclude(event):
            continue
        if event.event_id in cancelled_ids:
            continue
        if event.settlement_date < request_date and event.status == "settled":
            continue
        if event.settlement_date > horizon_end:
            continue

        amount = overrides.get(event.event_id, event.amount)
        if amount is None:
            continue

        amount_home = converter.convert(amount, event.currency, profile.home_currency, event.settlement_date)
        dedupe_key = (event.event_id, event.settlement_date, event.direction, amount_home)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        include = False
        if event.settlement_date >= request_date:
            if _include_credit(event):
                include = True
            elif _include_debit(event):
                include = True

        resolved.append(
            ResolvedEvent(
                event_id=event.event_id,
                category=event.category,
                direction=event.direction,
                amount_home=amount_home,
                settlement_date=event.settlement_date,
                status=event.status,
                flexibility=event.flexibility,
                minimum_allowed_amount=event.minimum_allowed_amount,
                source="event",
                include_in_forecast=include,
            )
        )
    return resolved
