from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from itertools import combinations

from buy_or_wait.domain import PaymentLeg, PlanCandidate, SpendingChange
from buy_or_wait.finance.forecast import ForecastEngine
from buy_or_wait.ingest.loader import PaymentOption, Profile, RequestRow


def _installment_legs(option: PaymentOption) -> list[PaymentLeg]:
    legs: list[PaymentLeg] = []
    current = option.first_payment_date
    for _ in range(option.number_of_payments):
        legs.append(PaymentLeg(payment_date=current, amount=option.payment_amount))
        if option.payment_frequency_days:
            current += timedelta(days=option.payment_frequency_days)
    return legs


def _months_span(request_date: date, option: PaymentOption) -> int:
    last_date = option.first_payment_date
    if option.number_of_payments > 1 and option.payment_frequency_days:
        last_date = option.first_payment_date + timedelta(
            days=option.payment_frequency_days * (option.number_of_payments - 1)
        )
    days = (last_date - request_date).days
    return max(1, (days + 29) // 30)


class PlanEnumerator:
    def __init__(self, forecast: ForecastEngine):
        self.forecast = forecast

    def _eligible_spending_changes(self, profile: Profile, request: RequestRow) -> list[SpendingChange]:
        changes: list[SpendingChange] = []
        historical = self.forecast.dataset.events_by_user.get(request.user_id, [])
        seen: set[str] = set()
        for event in sorted(historical, key=lambda e: e.settlement_date, reverse=True):
            if event.settlement_date > request.request_date:
                continue
            if event.flexibility not in {"stoppable", "reducible", "reducible_or_stoppable"}:
                continue
            if event.category in profile.expense_categories_to_protect:
                continue
            if event.event_id in seen:
                continue
            seen.add(event.event_id)
            if event.flexibility in {"stoppable", "reducible_or_stoppable"}:
                if event.category in profile.expense_categories_user_is_willing_to_stop:
                    changes.append(SpendingChange(action="stop", event_id=event.event_id))
            if event.flexibility in {"reducible", "reducible_or_stoppable"}:
                if event.category in profile.expense_categories_user_is_willing_to_reduce:
                    minimum = event.minimum_allowed_amount or Decimal("0")
                    if event.amount is not None and event.amount > minimum:
                        reduced = minimum if minimum > 0 else (event.amount * Decimal("0.5")).quantize(Decimal("0.01"))
                        changes.append(
                            SpendingChange(action="reduce_to", event_id=event.event_id, new_amount=reduced)
                        )
            if len(changes) >= 12:
                break
        return changes

    def _spending_combos(self, changes: list[SpendingChange], max_changes: int = 3) -> list[list[SpendingChange]]:
        combos: list[list[SpendingChange]] = [[]]
        for change in changes[:8]:
            combos.append([change])
        for size in range(2, min(max_changes, 3) + 1):
            for combo in combinations(changes[:8], size):
                stops = {c.event_id for c in combo if c.action == "stop"}
                reduces = {c.event_id for c in combo if c.action == "reduce_to"}
                if stops & reduces:
                    continue
                combos.append(list(combo))
        unique: list[list[SpendingChange]] = []
        seen: set[tuple] = set()
        for combo in combos:
            key = tuple(sorted((c.action, c.event_id, str(c.new_amount)) for c in combo))
            if key not in seen:
                seen.add(key)
                unique.append(combo)
        return unique

    def enumerate(
        self,
        profile: Profile,
        request: RequestRow,
        payment_options: list[PaymentOption],
        amount_safe: Decimal,
        earliest_full: date | None,
        amount_overrides: dict[str, Decimal] | None = None,
    ) -> list[PlanCandidate]:
        candidates: list[PlanCandidate] = []
        methods = set(profile.payment_methods_user_will_consider)
        spending_pool = self._eligible_spending_changes(profile, request)

        for spending_changes in self._spending_combos(spending_pool):
            if "full_payment" in methods:
                legs = [PaymentLeg(payment_date=request.request_date, amount=request.requested_amount)]
                sim = self.forecast.simulate_plan(
                    profile, request, legs, spending_changes, amount_overrides
                )
                candidates.append(
                    PlanCandidate(
                        method="full_payment",
                        legs=legs,
                        total_paid=request.requested_amount,
                        spending_changes=spending_changes,
                        completes_by_deadline=request.request_date <= request.desired_completion_date,
                        safe=sim.safe,
                    )
                )

            if (
                request.allows_partial_payment
                and "partial_payment" in methods
                and Decimal("0") < amount_safe < request.requested_amount
                and earliest_full
                and earliest_full <= request.desired_completion_date
            ):
                remainder = (request.requested_amount - amount_safe).quantize(Decimal("0.01"))
                legs = [
                    PaymentLeg(payment_date=request.request_date, amount=amount_safe),
                    PaymentLeg(payment_date=earliest_full, amount=remainder),
                ]
                sim = self.forecast.simulate_plan(
                    profile, request, legs, spending_changes, amount_overrides
                )
                candidates.append(
                    PlanCandidate(
                        method="partial_payment",
                        legs=legs,
                        total_paid=request.requested_amount,
                        spending_changes=spending_changes,
                        completes_by_deadline=earliest_full <= request.desired_completion_date,
                        safe=sim.safe,
                    )
                )

            if "installments" in methods and profile.max_installment_months is not None:
                for option in payment_options:
                    if option.payment_method != "installments":
                        continue
                    if _months_span(request.request_date, option) > profile.max_installment_months:
                        continue
                    legs = _installment_legs(option)
                    last_date = legs[-1].payment_date
                    sim = self.forecast.simulate_plan(
                        profile, request, legs, spending_changes, amount_overrides
                    )
                    candidates.append(
                        PlanCandidate(
                            method="installments",
                            legs=legs,
                            total_paid=option.total_payable_amount,
                            spending_changes=spending_changes,
                            payment_option_id=option.payment_option_id,
                            completes_by_deadline=last_date <= request.desired_completion_date,
                            safe=sim.safe,
                        )
                    )

            if (
                "full_payment" in methods
                and earliest_full
                and earliest_full > request.request_date
            ):
                legs = [PaymentLeg(payment_date=earliest_full, amount=request.requested_amount)]
                sim = self.forecast.simulate_plan(
                    profile, request, legs, spending_changes, amount_overrides
                )
                candidates.append(
                    PlanCandidate(
                        method="wait",
                        legs=legs,
                        total_paid=request.requested_amount,
                        spending_changes=spending_changes,
                        completes_by_deadline=earliest_full <= request.desired_completion_date,
                        safe=sim.safe,
                    )
                )

        return candidates

    @staticmethod
    def rank(candidates: list[PlanCandidate]) -> list[PlanCandidate]:
        def sort_key(plan: PlanCandidate) -> tuple:
            return (
                0 if plan.completes_by_deadline else 1,
                0 if not plan.spending_changes else 1,
                plan.total_paid,
                plan.legs[0].payment_date if plan.legs else date.max,
                len(plan.legs) if plan.legs else 0,
                plan.payment_option_id or "",
            )

        return sorted([p for p in candidates if p.safe], key=sort_key)
