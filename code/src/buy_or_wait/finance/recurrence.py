from __future__ import annotations

import calendar
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from buy_or_wait.config import RecurrencePolicy
from buy_or_wait.evidence.models import EvidenceContext, IncomeSchedulePatch
from buy_or_wait.ingest.loader import FinancialEvent, normalize_description

VARIABLE_CATEGORIES = {"groceries", "transport", "dining"}
SPECULATIVE = ("commission", "bonus", "lottery", "refund", "arrears", "investment gain")
PAYROLL_ALIASES = {"payroll credit", "base salary", "next confirmed salary", "prorated first salary",
                   "payroll before leave", "payroll after returning from leave", "final employer payroll",
                   "previous employer payroll", "new employer payroll"}


def series_identity(event: FinancialEvent) -> str:
    description = normalize_description(event.description)
    if event.direction == "debit" and event.category in VARIABLE_CATEGORIES and event.status == "settled":
        description = "variable category spending"
    if event.direction == "credit" and event.category == "salary" and description in PAYROLL_ALIASES:
        description = "regular payroll"
    elif event.direction == "credit" and any(w in description for w in
            ("freelance", "contract payment", "project payment", "consulting invoice", "independent work", "client retainer")):
        # Separate recurring settlement days, while allowing clients/projects to change.
        description = f"independent earnings day {event.settlement_date.day}"
    return "|".join((event.direction, event.category, event.currency, description))


@dataclass
class RecurringSeries:
    series_key: str
    template_event_id: str
    category: str
    direction: str
    cadence_days: int
    amount: Decimal
    currency: str
    is_fixed: bool
    flexibility: str
    minimum_allowed_amount: Decimal | None
    anchor_day: int | None = None
    monthly: bool = False


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


def _apply_income_patches(
    series: RecurringSeries,
    projected_date: date,
    evidence: EvidenceContext,
) -> Decimal | None:
    if series.category != "salary" or series.direction != "credit":
        return series.amount
    amount = series.amount
    stopped = False
    for patch in evidence.income_patches:
        if patch.stop_after and projected_date > patch.stop_after:
            stopped = True
        if patch.resume_from:
            stopped = projected_date < patch.resume_from
        if (patch.amount is not None and patch.effective_from and projected_date >= patch.effective_from
                and (patch.effective_until is None or projected_date <= patch.effective_until)):
            if patch.currency and patch.currency != series.currency:
                raise ValueError("Salary amendment currency differs from recurring salary")
            amount = patch.amount
    return None if stopped else amount


def detect_recurring_series(
    events: list[FinancialEvent],
    as_of: date,
    policy: RecurrencePolicy,
    evidence: EvidenceContext | None = None,
) -> list[RecurringSeries]:
    evidence = evidence or EvidenceContext()
    groups: dict[tuple[str, str, str, str], list[FinancialEvent]] = defaultdict(list)
    explicit_future_salary_dates: set[tuple[str, date]] = set()

    for event in events:
        if event.settlement_date > as_of:
            if (event.category == "salary" and event.direction == "credit" and event.status == "scheduled"
                    and "confirmed" in event.description.lower()):
                groups[tuple(series_identity(event).split("|"))].append(event)
            continue
        if event.status != "settled" or event.event_id in evidence.suppressed_event_ids:
            continue
        if event.direction == "non_cash":
            continue
        if event.event_type == "investment_valuation":
            continue
        if "next confirmed salary" in event.description.lower():
            continue
        if event.direction == "credit" and any(w in event.description.lower() for w in SPECULATIVE):
            continue
        key = tuple(series_identity(event).split("|"))
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
                        currency=latest.currency,
                        is_fixed=True,
                        flexibility=latest.flexibility,
                        minimum_allowed_amount=latest.minimum_allowed_amount,
                        anchor_day=latest.settlement_date.day,
                        monthly=True,
                    )
                )
            continue

        dates = sorted({e.settlement_date for e in group})
        if len(dates) < policy.min_history:
            continue
        median_gap = _median_gap(dates)
        amounts = [evidence.amount_overrides.get(e.event_id, e.amount) for e in group]
        amounts = [a for a in amounts if a is not None]
        if not amounts:
            continue
        cv = _amount_cv(amounts)
        is_fixed = cv <= policy.amount_cv_threshold
        monthly = policy.monthly_days[0] <= median_gap <= policy.monthly_days[1]
        gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
        if sum(abs(g - median_gap) <= policy.day_tolerance for g in gaps) / len(gaps) < 0.75:
            continue
        if policy.weekly_days[0] <= median_gap <= policy.weekly_days[1]:
            cadence = int(round(median_gap))
        elif policy.biweekly_days[0] <= median_gap <= policy.biweekly_days[1]:
            cadence = int(round(median_gap))
        elif monthly:
            cadence = 30
        else:
            cadence = int(round(median_gap)) if 1 <= median_gap <= 35 else 0
        if cadence <= 0:
            continue

        latest = group[-1]
        if (latest.direction == "credit" and latest.status == "settled"
                and (as_of - latest.settlement_date).days > cadence + policy.day_tolerance):
            # An expected pay cycle was missed; history alone no longer confirms ongoing pay.
            continue
        if latest.direction == "credit" and any(w in latest.description.lower() for w in
                ("final employer", "seasonal", "peak-season", "temporary assignment", "previous employer")):
            continue
        forecast_amount = amounts[-1]
        if latest.direction == "credit":
            # Stable regular pay is supported by its most frequent recent settled amount.
            # Irregular income retains a conservative lower observed amount.
            forecast_amount = (latest.amount if latest.status == "scheduled" else
                               statistics.mode(amounts) if is_fixed or "payroll" in key[-1] else min(amounts[-3:]))
        elif latest.category in VARIABLE_CATEGORIES or not is_fixed:
            # Upper quartile is conservative without repeating exceptional one-off baskets.
            recent = sorted(amounts[-12:])
            forecast_amount = recent[(3 * len(recent) - 1) // 4]

        series_list.append(
            RecurringSeries(
                series_key="|".join(key),
                template_event_id=latest.event_id,
                category=latest.category,
                direction=latest.direction,
                cadence_days=cadence,
                amount=forecast_amount,
                currency=latest.currency,
                is_fixed=is_fixed,
                flexibility=latest.flexibility,
                minimum_allowed_amount=latest.minimum_allowed_amount,
                anchor_day=latest.settlement_date.day,
                monthly=monthly,
            )
        )

    return sorted(series_list, key=lambda s: s.series_key)


def _series_preferred(candidate: RecurringSeries, incumbent: RecurringSeries) -> bool:
    if candidate.is_fixed != incumbent.is_fixed:
        return candidate.is_fixed
    if candidate.monthly != incumbent.monthly:
        return candidate.monthly
    if candidate.cadence_days != incumbent.cadence_days:
        return candidate.cadence_days > incumbent.cadence_days
    if candidate.direction == "debit":
        return candidate.amount >= incumbent.amount
    return candidate.amount <= incumbent.amount


def _add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def project_series_dates(
    start: date,
    end: date,
    cadence_days: int,
    anchor: date,
    *,
    monthly: bool = False,
    anchor_day: int | None = None,
) -> list[date]:
    dates: list[date] = []
    if monthly and anchor_day:
        current = date(anchor.year, anchor.month, min(anchor_day, calendar.monthrange(anchor.year, anchor.month)[1]))
        while current < start:
            current = _add_months(current, 1)
            day = min(anchor_day, calendar.monthrange(current.year, current.month)[1])
            current = date(current.year, current.month, day)
        while current <= end:
            if current >= start:
                dates.append(current)
            next_month = _add_months(current, 1)
            day = min(anchor_day, calendar.monthrange(next_month.year, next_month.month)[1])
            current = date(next_month.year, next_month.month, day)
        return dates

    current = anchor
    while current < start:
        current += timedelta(days=cadence_days)
    while current <= end:
        if current >= start:
            dates.append(current)
        current += timedelta(days=cadence_days)
    return dates
