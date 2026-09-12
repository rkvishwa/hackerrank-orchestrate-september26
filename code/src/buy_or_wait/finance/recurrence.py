from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from buy_or_wait.config import RecurrencePolicy
from buy_or_wait.ingest.loader import FinancialEvent, normalize_description


@dataclass
class RecurringSeries:
    series_key: str
    template_event_id: str
    category: str
    direction: str
    cadence_days: int
    amount: Decimal
    is_fixed: bool
    flexibility: str
    minimum_allowed_amount: Decimal | None


def _amount_cv(amounts: list[Decimal]) -> float:
    floats = [float(a) for a in amounts if a is not None]
    if len(floats) < 2:
        return 0.0
    mean = statistics.mean(floats)
    if mean == 0:
        return 0.0
    return statistics.pstdev(floats) / abs(mean)


def _median_gap(dates: list[date]) -> float:
    if len(dates) < 2:
        return 0.0
    gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
    return statistics.median(gaps)


def detect_recurring_series(
    events: list[FinancialEvent],
    as_of: date,
    policy: RecurrencePolicy,
) -> list[RecurringSeries]:
    groups: dict[tuple[str, str, str, str], list[FinancialEvent]] = defaultdict(list)
    for event in events:
        if event.settlement_date > as_of:
            continue
        if event.status not in {"settled", "scheduled", "pending"}:
            continue
        if event.direction == "non_cash":
            continue
        if event.event_type == "investment_valuation":
            continue
        key = (
            event.direction,
            event.category,
            event.currency,
            normalize_description(event.description),
        )
        groups[key].append(event)

    series_list: list[RecurringSeries] = []
    for key, group in groups.items():
        group = sorted(group, key=lambda e: e.settlement_date)
        if len(group) < policy.min_history:
            if any(e.status == "scheduled" and e.event_type in {"income", "subscription"} for e in group):
                latest = group[-1]
                if latest.amount is None:
                    continue
                series_list.append(
                    RecurringSeries(
                        series_key="|".join(key),
                        template_event_id=latest.event_id,
                        category=latest.category,
                        direction=latest.direction,
                        cadence_days=30,
                        amount=latest.amount,
                        is_fixed=True,
                        flexibility=latest.flexibility,
                        minimum_allowed_amount=latest.minimum_allowed_amount,
                    )
                )
            continue

        dates = [e.settlement_date for e in group]
        median_gap = _median_gap(dates)
        amounts = [e.amount for e in group if e.amount is not None]
        if not amounts:
            continue
        cv = _amount_cv(amounts)
        is_fixed = cv <= policy.amount_cv_threshold
        if policy.weekly_days[0] <= median_gap <= policy.weekly_days[1]:
            cadence = int(round(median_gap))
        elif policy.biweekly_days[0] <= median_gap <= policy.biweekly_days[1]:
            cadence = int(round(median_gap))
        elif policy.monthly_days[0] <= median_gap <= policy.monthly_days[1]:
            cadence = 30
        else:
            cadence = int(round(median_gap)) if median_gap >= 7 else 0
        if cadence <= 0:
            continue

        latest = group[-1]
        forecast_amount = Decimal(str(statistics.median([float(a) for a in amounts])))
        if not is_fixed and latest.category in {"groceries", "transport", "utilities"}:
            forecast_amount = max(amounts)

        series_list.append(
            RecurringSeries(
                series_key="|".join(key),
                template_event_id=latest.event_id,
                category=latest.category,
                direction=latest.direction,
                cadence_days=cadence,
                amount=forecast_amount,
                is_fixed=is_fixed,
                flexibility=latest.flexibility,
                minimum_allowed_amount=latest.minimum_allowed_amount,
            )
        )
    return series_list


def project_series_dates(start: date, end: date, cadence_days: int, anchor: date) -> list[date]:
    dates: list[date] = []
    current = anchor
    while current < start:
        current += timedelta(days=cadence_days)
    while current <= end:
        if current >= start:
            dates.append(current)
        current += timedelta(days=cadence_days)
    return dates
