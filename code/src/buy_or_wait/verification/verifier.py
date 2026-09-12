from __future__ import annotations

from decimal import Decimal

from buy_or_wait.domain import OUTPUT_COLUMNS, DecisionResult, PlanCandidate
from buy_or_wait.ingest.loader import Profile, RequestRow


class OutputVerifier:
    @staticmethod
    def verify_request_row(request: RequestRow, result: DecisionResult) -> list[str]:
        errors: list[str] = []
        if result.request_id != request.request_id:
            errors.append("request_id mismatch")
        if not (Decimal("0") <= result.amount_safe_to_pay <= request.requested_amount):
            errors.append("amount_safe_to_pay out of bounds")
        if result.affordability_status == "affordable_now" and result.earliest_date_for_full_payment != request.request_date.isoformat():
            errors.append("affordable_now requires earliest_date=request_date")
        if result.recommended_payment_method == "not_recommended" and result.payment_plan != "none":
            errors.append("not_recommended requires payment_plan=none")
        if result.affordability_status == "not_affordable" and result.payment_plan != "none":
            errors.append("not_affordable requires payment_plan=none")
        if result.recommended_payment_method == "partial_payment" and result.affordability_status != "affordable_with_plan":
            errors.append("partial_payment requires affordable_with_plan")
        if result.recommended_payment_method == "wait" and result.affordability_status != "affordable_later":
            errors.append("wait requires affordable_later")
        return errors

    @staticmethod
    def verify_plan(request: RequestRow, plan: PlanCandidate) -> list[str]:
        errors: list[str] = []
        if not plan.legs and plan.method != "not_recommended":
            errors.append("empty plan legs")
        if plan.method == "partial_payment" and len(plan.legs) != 2:
            errors.append("partial plan must have two legs")
        if plan.method == "partial_payment":
            total = sum(leg.amount for leg in plan.legs)
            if total != request.requested_amount:
                errors.append("partial legs must sum to requested_amount")
        if len(plan.spending_changes) > 3:
            errors.append("too many spending changes")
        stops = {c.event_id for c in plan.spending_changes if c.action == "stop"}
        reduces = {c.event_id for c in plan.spending_changes if c.action == "reduce_to"}
        if stops & reduces:
            errors.append("stop and reduce on same event")
        return errors

    @staticmethod
    def verify_csv_header(header: list[str]) -> list[str]:
        if header != OUTPUT_COLUMNS:
            return [f"invalid header: expected {OUTPUT_COLUMNS}, got {header}"]
        return []
