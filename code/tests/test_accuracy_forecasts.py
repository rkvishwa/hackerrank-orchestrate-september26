from datetime import date, timedelta
from decimal import Decimal as D
import pytest

from buy_or_wait.evidence.models import EvidenceContext, IncomeSchedulePatch, RentPatch
from buy_or_wait.evidence.messages import MessageResolver
from buy_or_wait.ingest.loader import MessageRow
from test_correctness import event, forecast, DAY


def test_generic_confirmation_does_not_duplicate_named_employer_payroll():
    rows = [event(f"pay{m}", date(2025, m, 15), "500", description="International employer payroll",
                  category="salary", direction="credit") for m in (10, 11, 12)]
    rows.append(event("confirmed", date(2026, 1, 15), "500", description="Next confirmed salary",
                      category="salary", direction="credit", status="scheduled"))
    f, p, q = forecast(rows)
    credits = [c for c in f.build_cashflows(p, q) if c.direction == "credit"]
    assert [(c.flow_date, c.amount) for c in credits] == [
        (date(2026, m, 15), D("500")) for m in (1, 2, 3)]


def test_confirmed_resumption_restarts_monthly_pay_after_leave_gap():
    rows = [event(f"pay{m}", date(2025, m, 15), "500", description="Payroll before leave",
                  category="salary", direction="credit") for m in (6, 7)]
    rows.append(event("returned", date(2025, 12, 15), "500", description="Payroll after returning from leave",
                      category="salary", direction="credit"))
    f, p, q = forecast(rows)
    ctx = EvidenceContext(income_patches=[IncomeSchedulePatch(amount=D("550"),
        effective_from=date(2026, 1, 15), resume_from=date(2026, 1, 15), currency="INR")])
    credits = [c for c in f.build_cashflows(p, q, evidence=ctx) if c.direction == "credit"]
    assert [(c.flow_date, c.amount) for c in credits] == [
        (date(2026, m, 15), D("550")) for m in (1, 2, 3)]


@pytest.mark.parametrize("second_amount", ["200", "500"])
def test_matching_confirmation_retains_independent_second_income(second_amount):
    rows = [event(f"{name}{m}", date(2025, m, 15), amount, description=name,
                  category="salary", direction="credit")
            for name, amount in [("Primary household salary", "500"), ("Second household income", second_amount)]
            for m in (10, 11, 12)]
    rows.append(event("confirmed", date(2026, 1, 15), "500", description="Next confirmed salary",
                      category="salary", direction="credit", status="scheduled"))
    f, p, q = forecast(rows)
    january = [c for c in f.build_cashflows(p, q) if c.flow_date == date(2026, 1, 15)]
    assert len(january) == 2
    assert sum(c.amount for c in january) == D("500") + D(second_amount)


def test_issued_rent_balance_is_not_increased_again():
    rows = [event(f"rent{m}", date(2025, m, 5), "100", description="Monthly rent") for m in (11, 12)]
    rows.append(event("invoice", date(2026, 1, 10), None, description="Outstanding rent balance", status="scheduled"))
    f, p, q = forecast(rows)
    ctx = EvidenceContext(amount_overrides={"invoice": D("200")}, rent_patches=[RentPatch(D("1.12"), DAY)])
    flows = f.build_cashflows(p, q, evidence=ctx)
    assert next(c.amount for c in flows if c.source == "invoice") == D("200")
    assert [c.amount for c in flows if c.source.startswith("series:")] == [D("112")] * 3


def test_ninety_day_window_contains_exactly_ninety_calendar_dates():
    rows = [event("last", DAY + timedelta(days=89), "100", status="scheduled"),
            event("outside", DAY + timedelta(days=90), "900", status="scheduled")]
    f, p, q = forecast(rows)
    flows = f.build_cashflows(p, q)
    assert [c.source for c in flows] == ["last"]
    assert f.max_safe_payment(p, q) == q.requested_amount


def test_pending_platform_earnings_do_not_become_future_salary():
    rows = [event(f"gig{m}", date(2025, m, 15), "500", description="Driver platform payout",
                  category="salary", direction="credit") for m in (10, 11, 12)]
    rows.append(event("settled", date(2026, 1, 2), "200", description="Driver platform payout",
                      category="salary", direction="credit"))
    f, p, q = forecast(rows)
    message = MessageRow("message", "u", "r", "", "2025-12-30T00:00:00Z", "provider",
        "The next platform payout is still pending. App earnings can change until the payout is closed.")
    ctx = MessageResolver(f.dataset, f.settings)._resolve_message(message, DAY)
    credits = [c for c in f.build_cashflows(p, q, evidence=ctx) if c.direction == "credit"]
    assert [(c.source, c.amount) for c in credits] == [("settled", D("200"))]


def test_salary_date_amendment_changes_one_occurrence_only():
    rows = [event(f"pay{m}", date(2025, m, 15), "500", description="Primary household salary",
                  category="salary", direction="credit") for m in (10, 11, 12)]
    rows.append(event("confirmed", date(2026, 1, 15), "500", description="Next confirmed salary",
                      category="salary", direction="credit", status="scheduled"))
    f, p, q = forecast(rows)
    message = MessageRow("message", "u", "r", "", "2025-12-30T00:00:00Z", "employer",
                        "Your confirmed salary is now expected on 2026-01-23. Use the revised date.")
    ctx = MessageResolver(f.dataset, f.settings)._resolve_message(message, DAY)
    credits = [c for c in f.build_cashflows(p, q, evidence=ctx) if c.direction == "credit"]
    assert [(c.flow_date, c.amount) for c in credits] == [
        (date(2026, 1, 23), D("500")), (date(2026, 2, 15), D("500")), (date(2026, 3, 15), D("500"))]


def test_one_confirmed_payment_without_history_does_not_create_recurring_income():
    f, p, q = forecast([event("confirmed", date(2026, 1, 15), "500", description="Next confirmed salary",
                            category="salary", direction="credit", status="scheduled")])
    assert [(c.flow_date, c.amount) for c in f.build_cashflows(p, q)] == [(date(2026, 1, 15), D("500"))]


def test_prorated_first_pay_and_confirmed_next_cycle_establish_monthly_payroll():
    f, p, q = forecast([
        event("first", date(2025, 12, 15), "200", description="Prorated first salary",
              category="salary", direction="credit"),
        event("confirmed", date(2026, 1, 15), "500", description="Next confirmed salary",
              category="salary", direction="credit", status="scheduled")])
    assert [(c.flow_date, c.amount) for c in f.build_cashflows(p, q)] == [
        (date(2026, m, 15), D("500")) for m in (1, 2, 3)]


def test_recent_payday_shift_confirmed_for_next_cycle_replaces_old_calendar():
    rows = [event(f"pay{m}", date(2025, m, 15), "500", description="Payroll credit",
                  category="salary", direction="credit") for m in (9, 10, 11)]
    rows.append(event("latest", date(2025, 12, 23), "500", description="Payroll credit",
                      category="salary", direction="credit"))
    f, p, q = forecast(rows)
    ctx = EvidenceContext(income_patches=[IncomeSchedulePatch(original_date=date(2026, 1, 15),
                                                             payment_date=date(2026, 1, 23))])
    assert [(c.flow_date, c.amount) for c in f.build_cashflows(p, q, evidence=ctx)] == [
        (date(2026, m, 23), D("500")) for m in (1, 2, 3)]
