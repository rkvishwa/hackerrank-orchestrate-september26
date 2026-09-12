"""Experimental calendar-window estimator. Not used by the default engine.

The rule is fixed before validation: three complete 30-day observation windows,
at least two known occurrences in each, nearest-rank upper quartile of their
average occurrence amounts, rounded upward to a cent. Sparse, constant and
non-routine series retain the production estimate. No public answers are inputs.
"""
from collections import defaultdict
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal, ROUND_CEILING

from buy_or_wait.finance.forecast import ForecastEngine
from buy_or_wait.finance.recurrence import VARIABLE_CATEGORIES


def calendar_window_estimate(series, history, as_of):
    audit = {"control_amount": str(series.amount), "windows": [], "eligible": False}
    if series.direction != "debit" or series.category not in VARIABLE_CATEGORIES:
        return series.amount, {**audit, "reason": "not frequent routine variable spending"}
    members = [e for e in history if e.event_id in series.member_event_ids and e.status == "settled"
               and e.event_date < as_of and e.settlement_date < as_of]
    if len({e.user_id for e in members}) > 1:
        raise ValueError("Mixed user histories in expense estimator")
    if not members or any(e.amount is None for e in members):
        return series.amount, {**audit, "reason": "missing observed amounts"}
    if len({e.currency for e in members}) != 1:
        raise ValueError("Mixed currencies in one recurring obligation")
    if min(e.settlement_date for e in members) > as_of - timedelta(days=90) + timedelta(days=series.cadence_days - 1):
        return series.amount, {**audit, "reason": "first window is not covered by series history"}
    by_day = defaultdict(lambda: Decimal(0))
    for event in members:
        by_day[event.settlement_date] += event.amount
    if len(set(by_day.values())) <= 1:
        return series.amount, {**audit, "reason": "constant amounts"}
    averages = []
    for age in (90, 60, 30):
        start = as_of - timedelta(days=age)
        end = start + timedelta(days=30)
        values = [amount for day, amount in sorted(by_day.items()) if start <= day < end]
        expected_dates = {start + timedelta(days=i) for i in range(30)
                          if (start + timedelta(days=i) - max(by_day)).days % series.cadence_days == 0}
        observed_dates = {day for day in by_day if start <= day < end}
        audit["windows"].append({"start": str(start), "end_exclusive": str(end),
                                 "occurrences": len(values), "total": str(sum(values, Decimal(0)))})
        if len(values) < 2:
            return series.amount, {**audit, "reason": "fewer than two occurrences in a window"}
        if observed_dates != expected_dates:
            return series.amount, {**audit, "reason": "window has missing or off-cadence observations"}
        averages.append(sum(values, Decimal(0)) / len(values))
    # ceil(0.75 * 3) = 3: the largest of the three observed window averages.
    estimate = max(averages).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    return estimate, {**audit, "eligible": True, "candidate_amount": str(estimate),
                      "reason": "upper quartile of three 30-day average occurrence costs"}


class CalendarWindowForecast(ForecastEngine):
    def _series_for_user(self, user_id, as_of, evidence):
        from buy_or_wait.finance.events import effective_event
        original = super()._series_for_user(user_id, as_of, evidence)
        history = [effective_event(e, evidence) for e in self.dataset.events_by_user.get(user_id, [])]
        result = []
        for series in original:
            amount, audit = calendar_window_estimate(series, history, as_of)
            result.append(replace(series, amount=amount,
                estimator="calendar_window_q75" if audit["eligible"] else series.estimator))
        return result


def calendar_window_engine(dataset, settings):
    from buy_or_wait.engine import DecisionEngine
    from buy_or_wait.plans.enumerator import PlanEnumerator
    from buy_or_wait.verification.verifier import OutputVerifier
    engine = DecisionEngine(dataset, settings)
    engine.forecast = CalendarWindowForecast(dataset, settings)
    engine.enumerator = PlanEnumerator(engine.forecast)
    engine.verifier = OutputVerifier(engine.forecast)
    return engine
