from __future__ import annotations

from buy_or_wait.domain import OUTPUT_COLUMNS
from buy_or_wait.verification.verifier import OutputVerifier


def test_output_columns_exact():
    assert OUTPUT_COLUMNS == [
        "request_id",
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation",
    ]


def test_header_validation():
    assert not OutputVerifier.verify_csv_header(OUTPUT_COLUMNS)
    assert OutputVerifier.verify_csv_header(["bad"])
