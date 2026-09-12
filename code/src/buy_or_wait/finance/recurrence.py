from __future__ import annotations

import calendar
import statistics
from collections import defaultdict, Counter
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
                   }
PLATFORM_INCOME = ("platform payout", "app earnings", "marketplace payout", "gig earnings")


def series_identity(event: FinancialEvent) -> str:
    description = normalize_description(event.description)
    document_or_exception = any(word in description.split() for word in
                               ("invoice", "airline", "flight", "ticket", "wallet", "authorization"))
    if (event.direction == "debit" and event.category in VARIABLE_CATEGORIES
            and event.status == "settled" and not document_or_exception):
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
    member_event_ids: tuple[str, ...] = ()
    estimator: str | None = None
    cancellation_event_ids: tuple[str, ...] = ()


def routine_members(group):
    """A new merchant can join a routine, but cannot redefine its schedule.

    Repeated descriptions establish the cadence. A novel description must land
    on that cadence and not be an exceptional basket relative to that history.
    This uses only the current user's history, never other users or sample answers.
    """
    if not group or group[0].direction != "debit" or group[0].category not in VARIABLE_CATEGORIES:
        return group
    counts = Counter(normalize_description(e.description) for e in group)
    primary = [e for e in group if counts[normalize_description(e.description)] >= 2]
    dates = sorted({e.settlement_date for e in primary})
    if len(dates) < 3:
        return group
    gap = _median_gap(dates)
    if gap <= 0 or int(gap) != gap:
        return group
    usual = [e.amount for e in primary if e.amount is not None]
    ceiling = max(usual) * 3 if usual else None
    all_dates = sorted({e.settlement_date for e in group})
    all_gaps = {(b - a).days for a, b in zip(all_dates, all_dates[1:])}
    if len(all_gaps) == 1:
        # Merchant choice is not a payment schedule. Alternating a favourite
        # merchant with other shops can make the favourite recur every second
        # cycle. Preserve the complete, regular spending cadence in that case.
        return [e for e in group if e in primary or
                e.amount is None or ceiling is None or e.amount <= ceiling]
    return [e for e in group if e in primary or
            ((e.settlement_date - dates[-1]).days % int(gap) == 0
             and (e.amount is None or ceiling is None or e.amount <= ceiling))]


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
        if not income_patch_applies(series, patch):
            continue
        identity = getattr(series, "series_key", getattr(series, "description", "")).lower()
        if patch.unconfirmed_variable_income and any(term in identity for term in PLATFORM_INCOME):
            return None
        if patch.stop_after and projected_date > patch.stop_after:
            stopped = True
        if patch.resume_from and not patch.ambiguous_target:
            stopped = projected_date < patch.resume_from
        if (patch.amount is not None and patch.effective_from and projected_date >= patch.effective_from
                and (patch.effective_until is None or projected_date <= patch.effective_until)):
            if patch.currency and patch.currency != series.currency:
                raise ValueError("Salary amendment currency differs from recurring salary")
            amount = min(amount, patch.amount) if patch.ambiguous_target else patch.amount
    return None if stopped else amount


def income_patch_applies(item, patch: IncomeSchedulePatch) -> bool:
    if hasattr(item, "event_id") and patch.target_event_ids is not None:
        return item.event_id in patch.target_event_ids
    identity = getattr(item, "series_key", None) or series_identity(item)
    return patch.target_series_keys is None or identity in patch.target_series_keys


def income_payment_date(item, original_date: date, evidence: EvidenceContext) -> date:
    if item.category == "salary" and item.direction == "credit":
        for patch in evidence.income_patches:
            if (income_patch_applies(item, patch) and patch.payment_date
                    and patch.original_date == original_date):
                original_date = max(original_date, patch.payment_date) if patch.ambiguous_target else patch.payment_date
    return original_date


def detect_recurring_series(
    events: list[FinancialEvent],
    as_of: date,
    policy: RecurrencePolicy,
    evidence: EvidenceContext | None = None,
) -> list[RecurringSeries]:
    evidence = evidence or EvidenceContext()
    from buy_or_wait.finance.income import associate_income
    associations = associate_income(events, as_of, evidence)
    groups: dict[tuple[str, str, str, str], list[FinancialEvent]] = defaultdict(list)
    confirmed = [e for e in events if e.status == "scheduled" and e.settlement_date >= as_of
                 and e.category == "salary" and e.direction == "credit" and "confirmed" in e.description.lower()]
    for event in events:
        if event.settlement_date >= as_of:
            continue
        if event.status != "settled" or event.event_id in evidence.suppressed_event_ids:
            continue
        if event.event_id in evidence.nonrecurring_event_ids:
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
        group = routine_members(sorted(group, key=lambda e: (e.settlement_date, e.event_id)))
        if len(group) == 1 and group[0].direction == "credit" and group[0].category == "salary":
            previous = group[0]
            following = [e for e in confirmed if e.currency == previous.currency
                         and e.event_id in associations
                         and associations[e.event_id].matched_series_key == "|".join(key)
                         and e.settlement_date.day == previous.settlement_date.day
                         and 26 <= (e.settlement_date - previous.settlement_date).days <= 35]
            if len(following) == 1:
                # A first (possibly prorated) payment plus a confirmed next
                # monthly cycle supports regular payroll; a lone future row does not.
                group = [previous, following[0]]
        if len(group) < policy.min_history:
            continue

        dates = sorted({e.settlement_date for e in group})
        if len(dates) < policy.min_history:
            continue
        # A cancelled occurrence supplies a scheduled date, never income or
        # an expense amount. It can explain a gap between paid occurrences.
        cancelled_occurrences = [e for e in events
                           if e.status == "cancelled" and series_identity(e) == "|".join(key)
                           and (e.event_id not in evidence.event_patches
                                or evidence.event_patches[e.event_id].cancel_scope == "occurrence")
                           and dates[0] < e.settlement_date < dates[-1]]
        cancelled_dates = {e.settlement_date for e in cancelled_occurrences}
        dates = sorted(set(dates) | cancelled_dates)
        median_gap = _median_gap(dates)
        amounts = [evidence.amount_overrides.get(e.event_id, e.amount) for e in group]
        amounts = [a for a in amounts if a is not None]
        if group[-1].direction == "debit":
            by_date = defaultdict(lambda: Decimal("0"))
            for e in group:
                value = evidence.amount_overrides.get(e.event_id, e.amount)
                if value is not None:
                    by_date[e.settlement_date] += value
            amounts = [by_date[d] for d in sorted(by_date)]
        if not amounts:
            continue
        cv = _amount_cv(amounts)
        is_fixed = cv <= policy.amount_cv_threshold
        monthly = policy.monthly_days[0] <= median_gap <= policy.monthly_days[1]
        gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
        resumed = [p for p in evidence.income_patches if income_patch_applies(group[-1], p)
                   and not p.ambiguous_target and p.resume_from and p.amount is not None
                   and group[-1].category == "salary" and group[-1].direction == "credit"
                   and p.currency in {None, group[-1].currency}
                   and p.resume_from.day in {d.day for d in dates}]
        confirmed_monthly_resume = bool(resumed and len({d.day for d in dates}) == 1
                                        and all(g >= 28 for g in gaps))
        confirmed_calendar_shift = bool(len(gaps) >= 2 and all(26 <= g <= 35 for g in gaps[:-1])
            and any(income_patch_applies(group[-1], p) and not p.ambiguous_target
                    and p.payment_date and p.payment_date.day == dates[-1].day
                    and 26 <= (p.payment_date - dates[-1]).days <= 35 for p in evidence.income_patches))
        if confirmed_monthly_resume or confirmed_calendar_shift:
            monthly = True
        if not (confirmed_monthly_resume or confirmed_calendar_shift) and sum(abs(g - median_gap) <= policy.day_tolerance for g in gaps) / len(gaps) < 0.75:
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
        if (not confirmed_monthly_resume and latest.direction == "credit" and latest.status == "settled"
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
        elif latest.category in VARIABLE_CATEGORIES or len(set(amounts)) > 1:
            # Upper quartile is conservative without repeating exceptional one-off baskets.
            recent = sorted(amounts[-12:])
            forecast_amount = recent[(3 * len(recent) - 1) // 4]

        anchor_day = latest.settlement_date.day
        if monthly and latest.direction == "credit":
            anchor_day = statistics.mode([d.day for d in dates])
            if any(income_patch_applies(latest, p) and not p.ambiguous_target
                   and p.payment_date and p.payment_date.day == latest.settlement_date.day
                   and 26 <= (p.payment_date - latest.settlement_date).days <= 35
                   for p in evidence.income_patches):
                # A recently shifted payday corroborated by the next confirmed
                # cycle supersedes the older calendar pattern.
                anchor_day = latest.settlement_date.day

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
                anchor_day=anchor_day,
                monthly=monthly,
                member_event_ids=tuple(e.event_id for e in group),
                cancellation_event_ids=tuple(sorted(e.event_id for e in cancelled_occurrences)),
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
