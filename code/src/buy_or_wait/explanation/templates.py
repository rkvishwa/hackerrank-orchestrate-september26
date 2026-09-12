from __future__ import annotations

from decimal import Decimal

from buy_or_wait.domain import PlanCandidate
from buy_or_wait.ingest.loader import Profile, RequestRow


def _fmt(amount: Decimal) -> str:
    if amount == amount.to_integral():
        return f"{amount:.2f}".rstrip("0").rstrip(".")
    return f"{amount:,.2f}".replace(",", "_").replace("_", ",")


def build_explanation(
    profile: Profile,
    request: RequestRow,
    plan: PlanCandidate,
    amount_safe: Decimal,
    earliest_full: str,
    affordability_status: str,
    evidence_notes: list[str] | None = None,
    forecast_horizon: int = 90,
) -> str:
    ccy = profile.home_currency
    minimum = profile.minimum_balance_to_keep

    if plan.method == "not_recommended":
        return (
            f"Do not make this payment by {request.desired_completion_date.isoformat()}. "
            f"No eligible plan meets that deadline while protecting the {ccy} {_fmt(minimum)} minimum. "
            f"Baseline safe payment today is {ccy} {_fmt(amount_safe)}. "
            + (f"Single-payment capacity is first available on {earliest_full}." if earliest_full
               else f"No safe full-payment date was found within {forecast_horizon} days.")
        )

    if plan.method == "full_payment":
        if plan.spending_changes:
            parts = []
            for change in plan.spending_changes:
                if change.action == "stop":
                    parts.append(f"Stop {change.event_id}")
                else:
                    parts.append(f"Reduce {change.event_id} to {ccy} {_fmt(change.new_amount)}")
            prefix = ", ".join(parts) + ", then "
        else:
            prefix = ""
        return (
            f"{prefix}Pay {ccy} {_fmt(request.requested_amount)} on {plan.legs[0].payment_date.isoformat()}. "
            f"This leaves at least {ccy} {_fmt(minimum)} available over the next {forecast_horizon} days."
        )

    if plan.method == "partial_payment":
        today = plan.legs[0].amount
        later = plan.legs[1].amount
        later_date = plan.legs[1].payment_date.isoformat()
        return (
            f"Pay {ccy} {_fmt(today)} today and the remaining {ccy} {_fmt(later)} on {later_date}. "
            f"This completes the full request and keeps the {ccy} {_fmt(minimum)} minimum protected."
        )

    if plan.method == "installments":
        count = len(plan.legs)
        amount = plan.legs[0].amount
        start = plan.legs[0].payment_date.isoformat()
        return (
            f"Use {count} installments of {ccy} {_fmt(amount)}, starting {start}. "
            f"This leaves at least {ccy} {_fmt(minimum)} available."
        )

    if plan.method == "wait":
        pay_date = plan.legs[0].payment_date.isoformat()
        return (
            f"Pay {ccy} {_fmt(request.requested_amount)} in full on {pay_date}. "
            f"Paying earlier would take the balance below the {ccy} {_fmt(minimum)} minimum."
        )

    return "No safe recommendation available."
