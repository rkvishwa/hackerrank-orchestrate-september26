from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import date, timedelta
from decimal import Decimal

from buy_or_wait.config import RecurrencePolicy, Settings
from buy_or_wait.domain import PaymentLeg, SpendingChange
from buy_or_wait.evidence.models import EvidenceContext
from buy_or_wait.finance.currency import CurrencyConverter
from buy_or_wait.finance.events import ResolvedEvent, resolve_user_events, effective_event
from buy_or_wait.finance.recurrence import (
    RecurringSeries,
    _apply_income_patches,
    detect_recurring_series,
    project_series_dates,
    income_payment_date,
)
from buy_or_wait.ingest.loader import Dataset, Profile, RequestRow, normalize_description


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
        self._series_cache: dict[tuple[str, str, str], list[RecurringSeries]] = {}
        self._flow_cache: dict[tuple, list[CashFlow]] = {}
        self._income_cache = {}

    def income_associations(self, user_id, as_of, evidence):
        from buy_or_wait.finance.income import associate_income
        key = (user_id, as_of, repr(evidence))
        if key not in self._income_cache:
            self._income_cache[key] = associate_income(
                [effective_event(e, evidence) for e in self.dataset.events_by_user.get(user_id, [])],
                as_of, evidence)
        return self._income_cache[key]

    def _series_for_user(self, user_id: str, as_of: date, evidence: EvidenceContext) -> list[RecurringSeries]:
        evidence_key = repr(evidence)
        key = (user_id, as_of.isoformat(), evidence_key)
        if key not in self._series_cache:
            effective = [effective_event(e, evidence)
                         for e in self.dataset.events_by_user.get(user_id, [])]
            historical = [e for e in effective
                if (e.settlement_date < as_of and e.status in {"settled", "cancelled"}) or (
                    e.status == "scheduled" and e.category == "salary" and "confirmed" in e.description.lower())]
            self._series_cache[key] = detect_recurring_series(historical, as_of, self.policy, evidence)
        return self._series_cache[key]

    def _cancelled_commitment(self, user_id, series_key, day, evidence):
        from buy_or_wait.finance.recurrence import series_identity
        return any(p.cancel and p.cancel_scope == "series"
                   and (p.cancel_from is None or day >= p.cancel_from)
                   and raw is not None and raw.user_id == user_id
                   and series_identity(raw) == series_key
                   for eid, p in evidence.event_patches.items()
                   for raw in [self.dataset.events_by_id.get(eid)])

    def build_cashflows(
        self,
        profile: Profile,
        request: RequestRow,
        amount_overrides: dict[str, Decimal] | None = None,
        spending_changes: list[SpendingChange] | None = None,
        evidence: EvidenceContext | None = None,
    ) -> list[CashFlow]:
        evidence = evidence or EvidenceContext()
        cache_key = (request.user_id, request.request_date, profile.home_currency,
                     repr(evidence), repr(amount_overrides), repr(spending_changes))
        if cache_key in self._flow_cache:
            return self._flow_cache[cache_key]
        if amount_overrides:
            evidence = replace(evidence,
                amount_overrides={**evidence.amount_overrides, **amount_overrides},
                event_patches=evidence.event_patches,
                suppressed_event_ids=evidence.suppressed_event_ids,
                income_patches=evidence.income_patches,
                rent_patches=evidence.rent_patches,
                notes=evidence.notes,
                unresolved_mandatory_debits=evidence.unresolved_mandatory_debits,
            )

        horizon_end = request.request_date + timedelta(days=self.settings.forecast_horizon_days - 1)
        events = resolve_user_events(
            self.dataset,
            profile,
            request.user_id,
            request.request_date,
            horizon_end,
            amount_overrides=evidence.amount_overrides,
            evidence=evidence,
        )
        spending_changes = spending_changes or []
        stopped_events = {c.event_id for c in spending_changes if c.action == "stop"}
        reduced_events = {c.event_id: c.new_amount for c in spending_changes if c.action == "reduce_to"}

        flows: list[CashFlow] = []
        known_projection_keys: set[tuple[date, str, str, str]] = set()
        associations = self.income_associations(request.user_id, request.request_date, evidence)

        for event in events:
            if not event.include_in_forecast:
                continue
            if self._cancelled_commitment(request.user_id, event.series_key, event.settlement_date, evidence):
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
            series_key = event.series_key
            association = associations.get(event.event_id)
            if association:
                # Ambiguous confirmations are handled as an occurrence overlap,
                # not by pretending their generic label identifies employment.
                if not association.matched_series_key:
                    continue
                series_key = association.matched_series_key
            known_projection_keys.add(
                (event.settlement_date, event.direction, event.category, series_key)
            )

        for explicit in evidence.confirmed_flows:
            day = explicit["date"]
            if day < request.request_date or day > horizon_end:
                continue
            amount = self.converter.convert(explicit["amount"], explicit["currency"], profile.home_currency, day)
            flows.append(CashFlow(day, amount, explicit["direction"], explicit["category"],
                                  explicit["direction"] == "debit", False, "evidence:" + explicit["source"]))

        for series in self._series_for_user(request.user_id, request.request_date, evidence):
            if series.template_event_id in stopped_events:
                continue
            anchor = next(
                (
                    e.settlement_date
                    for e in self.dataset.events_by_user.get(request.user_id, [])
                    if e.event_id == series.template_event_id
                ),
                request.request_date,
            )
            for projected_date in project_series_dates(
                request.request_date,
                horizon_end,
                series.cadence_days,
                anchor,
                monthly=series.monthly,
                anchor_day=series.anchor_day,
            ):
                original_projection_date = projected_date
                projected_date = income_payment_date(series, projected_date, evidence)
                if not request.request_date <= projected_date <= horizon_end:
                    continue
                if self._cancelled_commitment(request.user_id, series.series_key, projected_date, evidence):
                    continue
                dedupe_key = (projected_date, series.direction, series.category, series.series_key)
                if dedupe_key in known_projection_keys:
                    continue
                if series.category == "salary" and series.direction == "credit":
                    overlapping = [associations[e.event_id] for e in events
                                   if e.event_id in associations and e.include_in_forecast
                                   and e.settlement_date == projected_date
                                   and series.series_key in associations[e.event_id].candidate_series_keys]
                    if overlapping:
                        continue
                # An explicit amended occurrence replaces its original recurrence date.
                template = self.dataset.events_by_id[series.template_event_id]
                from buy_or_wait.finance.recurrence import series_identity
                replaced = any(
                    series_identity(raw) == series.series_key and raw.settlement_date == projected_date
                    and (raw.event_id in evidence.suppressed_event_ids or raw.event_id in evidence.event_patches)
                    for raw in self.dataset.events_by_user.get(request.user_id, [])
                    if raw.settlement_date >= request.request_date
                )
                if replaced:
                    continue
                amount_native = _apply_income_patches(series, projected_date, evidence)
                if amount_native is None:
                    continue
                if series.category == "rent":
                    for patch in evidence.rent_patches:
                        if (projected_date >= patch.effective_from and
                                (patch.target_series_keys is None or series.series_key in patch.target_series_keys)):
                            amount_native = (amount_native * patch.multiplier).quantize(Decimal("0.01"))
                amount = self.converter.convert(
                    amount_native, series.currency, profile.home_currency, projected_date
                )
                if series.template_event_id in reduced_events and reduced_events[series.template_event_id] is not None:
                    amount = reduced_events[series.template_event_id]
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
        self._flow_cache[cache_key] = flows
        return flows

    def simulate_plan(
        self,
        profile: Profile,
        request: RequestRow,
        plan_legs: list[PaymentLeg],
        spending_changes: list[SpendingChange] | None = None,
        amount_overrides: dict[str, Decimal] | None = None,
        evidence: EvidenceContext | None = None,
        debit_before_credit: bool = False,
    ) -> SimulationResult:
        if evidence and evidence.unresolved_mandatory_debits:
            return SimulationResult(safe=False, min_balance=profile.current_available_balance)
        flows = self.build_cashflows(profile, request, amount_overrides, spending_changes, evidence)
        by_date: dict[date, list[tuple[str, CashFlow | PaymentLeg]]] = defaultdict(list)
        for flow in flows:
            by_date[flow.flow_date].append(("flow", flow))
        for leg in plan_legs:
            by_date[leg.payment_date].append(("plan", leg))

        balance = profile.current_available_balance
        minimum = profile.minimum_balance_to_keep
        min_seen = balance
        if balance < minimum:
            return SimulationResult(safe=False, min_balance=balance)

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
        evidence: EvidenceContext | None = None,
    ) -> Decimal:
        on_date = on_date or request.request_date
        if not self.simulate_plan(profile, request, [], spending_changes, amount_overrides, evidence).safe:
            return Decimal("0")
        low = Decimal("0")
        high = request.requested_amount
        best = Decimal("0")
        for _ in range(64):
            if low > high:
                break
            mid = ((low + high) / 2).quantize(Decimal("0.01"))
            legs = [PaymentLeg(payment_date=on_date, amount=mid)] if mid > 0 else []
            if self.simulate_plan(profile, request, legs, spending_changes, amount_overrides, evidence).safe:
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
        evidence: EvidenceContext | None = None,
    ) -> date | None:
        horizon_end = request.request_date + timedelta(days=self.settings.forecast_horizon_days - 1)
        if self.simulate_plan(
            profile,
            request,
            [PaymentLeg(payment_date=horizon_end, amount=request.requested_amount)],
            spending_changes,
            amount_overrides,
            evidence,
        ).safe:
            low = request.request_date
            high = horizon_end
            best: date | None = None
            while low <= high:
                mid = low + timedelta(days=(high - low).days // 2)
                legs = [PaymentLeg(payment_date=mid, amount=request.requested_amount)]
                if self.simulate_plan(profile, request, legs, spending_changes, amount_overrides, evidence).safe:
                    best = mid
                    high = mid - timedelta(days=1)
                else:
                    low = mid + timedelta(days=1)
            return best

        day = request.request_date
        while day <= horizon_end:
            legs = [PaymentLeg(payment_date=day, amount=request.requested_amount)]
            if self.simulate_plan(profile, request, legs, spending_changes, amount_overrides, evidence).safe:
                return day
            day += timedelta(days=1)
        return None
