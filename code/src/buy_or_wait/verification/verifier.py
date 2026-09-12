from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from buy_or_wait.domain import OUTPUT_COLUMNS, DecisionResult, PlanCandidate, PaymentLeg, SpendingChange
from buy_or_wait.evidence.models import EvidenceContext

VALID_STATUSES = {"affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"}
VALID_METHODS = {"full_payment", "partial_payment", "installments", "wait", "not_recommended"}


def parse_plan(value: str) -> list[PaymentLeg]:
    if value == "none":
        return []
    legs = []
    for part in value.split("|"):
        day, amount = part.split(":")
        number = Decimal(amount)
        if not number.is_finite() or number <= 0:
            raise ValueError("Payment amounts must be positive and finite")
        parsed = date.fromisoformat(day)
        if parsed.isoformat() != day:
            raise ValueError("Payment dates must use YYYY-MM-DD")
        legs.append(PaymentLeg(parsed, number))
    if [p.payment_date for p in legs] != sorted(p.payment_date for p in legs):
        raise ValueError("Payment plan must be chronological")
    return legs


def parse_spending(value: str) -> list[SpendingChange]:
    if value == "none":
        return []
    result = []
    for part in value.split("|"):
        fields = part.split(":")
        if len(fields) == 2 and fields[0] == "stop":
            result.append(SpendingChange("stop", fields[1]))
        elif len(fields) == 3 and fields[0] == "reduce_to":
            amount = Decimal(fields[2])
            if not amount.is_finite() or amount < 0:
                raise ValueError("Invalid reduction amount")
            result.append(SpendingChange("reduce_to", fields[1], amount))
        else:
            raise ValueError("Invalid spending change")
    if len(result) > 3 or len({c.event_id for c in result}) != len(result):
        raise ValueError("At most three distinct spending changes are allowed")
    return result


class OutputVerifier:
    def __init__(self, forecast=None):
        self.forecast = forecast

    def verify_request_row(self, request, result, profile=None, payment_options=None,
                           selected_plan=None, evidence=None) -> list[str]:
        errors = []
        if result.request_id != request.request_id:
            errors.append("request_id mismatch")
        if result.affordability_status not in VALID_STATUSES:
            errors.append("invalid affordability_status")
        if result.recommended_payment_method not in VALID_METHODS:
            errors.append("invalid recommended_payment_method")
        if not result.amount_safe_to_pay.is_finite() or not 0 <= result.amount_safe_to_pay <= request.requested_amount:
            errors.append("amount_safe_to_pay out of bounds")
        if not result.decision_explanation.strip():
            errors.append("decision_explanation is required")
        try:
            legs = parse_plan(result.payment_plan)
            changes = parse_spending(result.spending_changes_needed)
            earliest = date.fromisoformat(result.earliest_date_for_full_payment) if result.earliest_date_for_full_payment else None
        except (ValueError, InvalidOperation, TypeError):
            return errors + ["invalid plan, spending change or date"]
        method = result.recommended_payment_method
        status = result.affordability_status
        plan = PlanCandidate(method, legs, sum((leg.amount for leg in legs), Decimal("0")), changes)
        errors.extend(self.verify_plan(request, plan))
        if method == "not_recommended":
            if legs or changes or status != "not_affordable":
                errors.append("not_recommended requires not_affordable and no payments or changes")
        elif not legs:
            errors.append("recommended payment requires a plan")
        if status == "affordable_now":
            if (method != "full_payment" or changes or result.amount_safe_to_pay != request.requested_amount
                    or earliest != request.request_date or len(legs) != 1 or legs[0].payment_date != request.request_date):
                errors.append("inconsistent affordable_now")
        if method == "partial_payment":
            if status != "affordable_with_plan" or not request.allows_partial_payment:
                errors.append("partial payment is not eligible")
            if not 0 < result.amount_safe_to_pay < request.requested_amount:
                errors.append("partial payment requires a positive baseline smaller than request")
            if len(legs) == 2 and (legs[0].payment_date != request.request_date
                    or legs[0].amount != result.amount_safe_to_pay or legs[1].payment_date != earliest):
                errors.append("partial payment dates/amount differ from baseline fields")
        if method == "wait" and (status != "affordable_later" or changes or len(legs) != 1
                                or legs[0].payment_date <= request.request_date or legs[0].payment_date != earliest):
            errors.append("inconsistent wait plan")
        if method == "installments" and status != "affordable_with_plan":
            errors.append("installments require affordable_with_plan")
        if method == "full_payment" and status not in {"affordable_now", "affordable_with_plan"}:
            errors.append("invalid full-payment status")
        if method in {"full_payment", "wait"} and (len(legs) != 1 or plan.total_paid != request.requested_amount):
            errors.append("full payment must pay exactly the request")
        if profile:
            required = "full_payment" if method == "wait" else method
            if method != "not_recommended" and required not in profile.payment_methods_user_will_consider:
                errors.append("payment method conflicts with user preferences")
        if method == "installments":
            from buy_or_wait.plans.enumerator import _installment_legs, _months_span
            matches = [o for o in (payment_options or [])
                       if o.payment_method == "installments" and _installment_legs(o) == legs
                       and o.total_payable_amount == plan.total_paid]
            if not matches:
                errors.append("installments do not exactly match a supplied option")
            elif profile and (profile.max_installment_months is None or not any(
                    _months_span(request.request_date, o) <= profile.max_installment_months for o in matches)):
                errors.append("installment duration conflicts with preferences")
        if self.forecast and profile:
            if evidence is None:
                from buy_or_wait.evidence.resolver import EvidenceResolver
                evidence = EvidenceResolver(self.forecast.dataset, self.forecast.settings).resolve(request)
            allowed_series = {s.template_event_id: s for s in self.forecast._series_for_user(
                request.user_id, request.request_date, evidence) if s.direction == "debit"}
            for change in changes:
                event = self.forecast.dataset.events_by_id.get(change.event_id)
                series = allowed_series.get(change.event_id)
                if event is None or event.user_id != request.user_id or series is None:
                    errors.append("spending change must reference a recurring user expense")
                    continue
                if event.category in profile.expense_categories_to_protect:
                    errors.append("cannot change protected spending")
                if change.action == "stop":
                    if event.flexibility not in {"stoppable", "reducible_or_stoppable"} or event.category not in profile.expense_categories_user_is_willing_to_stop:
                        errors.append("stopping this expense is not permitted")
                else:
                    if event.flexibility not in {"reducible", "reducible_or_stoppable"} or event.category not in profile.expense_categories_user_is_willing_to_reduce:
                        errors.append("reducing this expense is not permitted")
                    minimum = self.forecast.converter.convert(event.minimum_allowed_amount or Decimal("0"),
                               event.currency, profile.home_currency, event.settlement_date)
                    original = self.forecast.converter.convert(series.amount, event.currency,
                               profile.home_currency, event.settlement_date)
                    if not minimum <= change.new_amount < original:
                        errors.append("reduction is outside the permitted amount range")
            safe_amount = self.forecast.max_safe_payment(profile, request, evidence=evidence)
            safe_date = self.forecast.earliest_full_payment_date(profile, request, evidence=evidence)
            if result.amount_safe_to_pay != safe_amount:
                errors.append("amount_safe_to_pay does not equal baseline capacity")
            if earliest != safe_date:
                errors.append("earliest_date_for_full_payment does not equal baseline capacity date")
            if legs and not self.forecast.simulate_plan(profile, request, legs, changes, evidence=evidence).safe:
                errors.append("payment plan breaches the minimum balance")
            horizon = request.request_date + timedelta(days=self.forecast.settings.forecast_horizon_days)
            if any(leg.payment_date > horizon for leg in legs):
                errors.append("payment outside verified forecast horizon")
        return list(dict.fromkeys(errors))

    @staticmethod
    def verify_plan(request, plan) -> list[str]:
        errors = []
        if plan.method != "not_recommended" and not plan.legs:
            errors.append("empty plan legs")
        if any(leg.payment_date < request.request_date or leg.payment_date > request.desired_completion_date for leg in plan.legs):
            errors.append("payment outside request date/deadline")
        if any(not leg.amount.is_finite() or leg.amount <= 0 for leg in plan.legs):
            errors.append("invalid payment amount")
        if plan.method == "partial_payment" and (len(plan.legs) != 2 or sum(leg.amount for leg in plan.legs) != request.requested_amount):
            errors.append("partial plan must have two payments summing to requested amount")
        if len(plan.spending_changes) > 3 or len({c.event_id for c in plan.spending_changes}) != len(plan.spending_changes):
            errors.append("spending changes must reference at most three distinct events")
        return errors

    @staticmethod
    def verify_csv_header(header):
        return [] if header == OUTPUT_COLUMNS else [f"invalid header: expected {OUTPUT_COLUMNS}, got {header}"]
