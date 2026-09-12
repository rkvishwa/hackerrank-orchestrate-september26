from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from functools import lru_cache

from buy_or_wait.config import RecurrencePolicy, Settings
from buy_or_wait.domain import PaymentLeg, SpendingChange
from buy_or_wait.finance.currency import CurrencyConverter
from buy_or_wait.finance.events import ResolvedEvent, resolve_user_events
from buy_or_wait.finance.recurrence import RecurringSeries, detect_recurring_series, project_series_dates
from buy_or_wait.ingest.loader import Dataset, Profile, RequestRow


@dataclass
class CashFlow:
    flow_date: date
    amount: Decimal
    direction: str
    category: str
    protected: bool
    flexible: bool
    source: str


@dataclass
class SimulationResult:
    safe: bool
    min_balance: Decimal


class ForecastEngine:
    def __init__(self, dataset: Dataset, settings: Settings | None = None):
        self.dataset = dataset
        self.settings = settings or Settings()
        self.converter = CurrencyConverter(dataset.exchange_rates)
        self.policy = self.settings.recurrence
        self._series_cache: dict[tuple[str, str], list[RecurringSeries]] = {}

    def _series_for_user(self, user_id: str, as_of: date) -> list[RecurringSeries]:
        key = (user_id, as_of.isoformat())
        if key not in self._series_cache:
            historical = [
                e
                for e in self.dataset.events_by_user.get(user_id, [])
                if e.settlement_date < as_of and e.status == "settled"
            ]
            self._series_cache[key] = detect_recurring_series(historical, as_of, self.policy)
        return self._series_cache[key]

    def build_cashflows(
        self,
        profile: Profile,
        request: RequestRow,
        amount_overrides: dict[str, Decimal] | None = None,
        spending_changes: list[SpendingChange] | None = None,
    ) -> list[CashFlow]:
        horizon_end = request.request_date + timedelta(days=self.settings.forecast_horizon_days)
        events = resolve_user_events(
            self.dataset,
            profile,
            request.user_id,
            request.request_date,
            horizon_end,
            amount_overrides=amount_overrides,
        )
        spending_changes = spending_changes or []
        stopped_events = {c.event_id for c in spending_changes if c.action == "stop"}
        reduced_events = {c.event_id: c.new_amount for c in spending_changes if c.action == "reduce_to"}

        flows: list[CashFlow] = []
        known_event_dates: set[tuple[date, str]] = set()

        for event in events:
            if not event.include_in_forecast:
                continue
            amount = event.amount_home
            if event.event_id in stopped_events:
                continue
            if event.event_id in reduced_events and reduced_events[event.event_id] is not None:
                amount = reduced_events[event.event_id]
            protected = event.category in profile.expense_categories_to_protect
            flexible = event.flexibility in {"stoppable", "reducible", "reducible_or_stoppable"}
            flows.append(
                CashFlow(
                    flow_date=event.settlement_date,
                    amount=amount,
                    direction=event.direction,
                    category=event.category,
                    protected=protected,
                    flexible=flexible,
                    source=event.event_id,
                )
            )
            known_event_dates.add((event.settlement_date, event.event_id))

        for series in self._series_for_user(request.user_id, request.request_date):
            if series.template_event_id in stopped_events:
                continue
            amount = series.amount
            if series.template_event_id in reduced_events and reduced_events[series.template_event_id] is not None:
                amount = reduced_events[series.template_event_id]
            anchor = next(
                (
                    e.settlement_date
                    for e in self.dataset.events_by_user.get(request.user_id, [])
                    if e.event_id == series.template_event_id
                ),
                request.request_date,
            )
            for projected_date in project_series_dates(
                request.request_date, horizon_end, series.cadence_days, anchor
            ):
                if (projected_date, series.template_event_id) in known_event_dates:
                    continue
                protected = series.category in profile.expense_categories_to_protect
                flexible = series.flexibility in {"stoppable", "reducible", "reducible_or_stoppable"}
                flows.append(
                    CashFlow(
                        flow_date=projected_date,
                        amount=amount,
                        direction=series.direction,
                        category=series.category,
                        protected=protected,
                        flexible=flexible,
                        source=f"series:{series.template_event_id}",
                    )
                )
        return flows

    def simulate_plan(
        self,
        profile: Profile,
        request: RequestRow,
        plan_legs: list[PaymentLeg],
        spending_changes: list[SpendingChange] | None = None,
        amount_overrides: dict[str, Decimal] | None = None,
        debit_before_credit: bool = False,
    ) -> SimulationResult:
        flows = self.build_cashflows(profile, request, amount_overrides, spending_changes)
        by_date: dict[date, list[tuple[str, CashFlow | PaymentLeg]]] = defaultdict(list)
        for flow in flows:
            by_date[flow.flow_date].append(("flow", flow))
        for leg in plan_legs:
            by_date[leg.payment_date].append(("plan", leg))

        balance = profile.current_available_balance
        minimum = profile.minimum_balance_to_keep
        min_seen = balance

        for day in sorted(by_date):
            items = by_date[day]

            def sort_key(item: tuple[str, CashFlow | PaymentLeg]) -> tuple:
                kind, payload = item
                if kind == "plan":
                    return (2, 0)
                flow = payload  # type: ignore[assignment]
                if flow.direction == "credit":
                    return (0 if not debit_before_credit else 1, 0 if flow.protected else 1)
                return (1 if not debit_before_credit else 0, 0 if flow.protected else 1)

            for _, payload in sorted(items, key=sort_key):
                if isinstance(payload, PaymentLeg):
                    balance -= payload.amount
                else:
                    balance += payload.amount if payload.direction == "credit" else -payload.amount
                min_seen = min(min_seen, balance)
                if balance < minimum:
                    return SimulationResult(safe=False, min_balance=min_seen)
        return SimulationResult(safe=True, min_balance=min_seen)

    def max_safe_payment(
        self,
        profile: Profile,
        request: RequestRow,
        on_date: date | None = None,
        spending_changes: list[SpendingChange] | None = None,
        amount_overrides: dict[str, Decimal] | None = None,
    ) -> Decimal:
        on_date = on_date or request.request_date
        if not self.simulate_plan(profile, request, [], spending_changes, amount_overrides).safe:
            return Decimal("0")
        low = Decimal("0")
        high = request.requested_amount
        best = Decimal("0")
        for _ in range(64):
            if low > high:
                break
            mid = ((low + high) / 2).quantize(Decimal("0.01"))
            legs = [PaymentLeg(payment_date=on_date, amount=mid)] if mid > 0 else []
            if self.simulate_plan(profile, request, legs, spending_changes, amount_overrides).safe:
                best = mid
                low = mid + Decimal("0.01")
            else:
                high = mid - Decimal("0.01")
        return min(best, request.requested_amount).quantize(Decimal("0.01"))

    def earliest_full_payment_date(
        self,
        profile: Profile,
        request: RequestRow,
        spending_changes: list[SpendingChange] | None = None,
        amount_overrides: dict[str, Decimal] | None = None,
    ) -> date | None:
        horizon_end = request.request_date + timedelta(days=self.settings.forecast_horizon_days)
        day = request.request_date
        while day <= horizon_end:
            legs = [PaymentLeg(payment_date=day, amount=request.requested_amount)]
            if self.simulate_plan(profile, request, legs, spending_changes, amount_overrides).safe:
                return day
            day += timedelta(days=1)
        return None
