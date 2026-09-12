from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Literal

AffordabilityStatus = Literal[
    "affordable_now",
    "affordable_with_plan",
    "affordable_later",
    "not_affordable",
]
PaymentMethod = Literal[
    "full_payment",
    "partial_payment",
    "installments",
    "wait",
    "not_recommended",
]

OUTPUT_COLUMNS = [
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation",
]

REQUEST_TYPES = {
    "purchase",
    "travel",
    "education",
    "family_transfer",
    "debt_repayment",
    "investment",
    "housing",
    "emergency_expense",
    "other",
}


@dataclass
class PaymentLeg:
    payment_date: date
    amount: Decimal


@dataclass
class SpendingChange:
    action: Literal["stop", "reduce_to"]
    event_id: str
    new_amount: Decimal | None = None


@dataclass
class PlanCandidate:
    method: PaymentMethod
    legs: list[PaymentLeg]
    total_paid: Decimal
    spending_changes: list[SpendingChange] = field(default_factory=list)
    payment_option_id: str | None = None
    completes_by_deadline: bool = True
    safe: bool = False


@dataclass
class DecisionResult:
    request_id: str
    amount_safe_to_pay: Decimal
    affordability_status: AffordabilityStatus
    recommended_payment_method: PaymentMethod
    payment_plan: str
    earliest_date_for_full_payment: str
    spending_changes_needed: str
    decision_explanation: str
    trace: dict = field(default_factory=dict)
