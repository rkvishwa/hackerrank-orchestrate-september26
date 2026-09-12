"""Source-based regressions; no public sample answers are used here."""
from dataclasses import replace
from datetime import date
from decimal import Decimal as D
from types import SimpleNamespace

import pytest

from buy_or_wait.config import Settings
from buy_or_wait.domain import PaymentLeg
from buy_or_wait.evidence.models import EvidenceContext, EventPatch
from buy_or_wait.finance.forecast import ForecastEngine
from test_correctness import event, setup, DAY


def model(rows=(), **kwargs):
    dataset, profile, request = setup(rows, **kwargs)
    return ForecastEngine(dataset, Settings(_env_file=None, llm_enabled=False,
                          deterministic_mode=True)), profile, request


def salary(eid, month, amount="500", employer="Employer A", *, future=False, day=15):
    return event(eid, date(2026 if future else 2025, month, day), amount,
                 description=f"{employer} {'confirmed salary' if future else 'payroll'}",
                 category="salary", direction="credit", status="scheduled" if future else "settled")


@pytest.mark.parametrize("message_patch", [False, True])
def test_cancelled_occurrence_bridges_cadence_without_amount_or_anchor(message_patch):
    rows = [event("oct", date(2025, 10, 5)),
            event("nov", date(2025, 11, 5), "9999", status="cancelled", flexibility="stoppable"),
            event("dec", date(2025, 12, 5))]
    f, p, q = model(rows)
    ctx = EvidenceContext(event_patches={"nov": EventPatch("nov", cancel=True, cancel_scope="occurrence")}
                          if message_patch else {})
    series = f._series_for_user("u", DAY, ctx)
    assert len(series) == 1
    assert series[0].member_event_ids == ("oct", "dec")
    assert series[0].cancellation_event_ids == ("nov",)
    assert series[0].template_event_id == "dec" and series[0].flexibility == "fixed"
    assert [(x.flow_date, x.amount) for x in f.build_cashflows(p, q, evidence=ctx)] == [
        (date(2026, m, 5), D("100")) for m in (1, 2, 3)]


def test_cancelled_record_restored_by_settlement_enters_history():
    from buy_or_wait.artifacts.evaluation import forecast_audit
    rows = [event("nov", date(2025, 11, 5)), event("dec", date(2025, 12, 5), status="cancelled")]
    f, p, q = model(rows)
    ctx = EvidenceContext(event_patches={"dec": EventPatch("dec", status="settled")})
    assert [x.amount for x in f.build_cashflows(p, q, evidence=ctx)] == [D("100")] * 3
    trace = forecast_audit(SimpleNamespace(dataset=f.dataset, forecast=f, settings=f.settings), q, ctx)
    assert trace["recurring_estimates"][0]["recent_observations"] == ["100", "100"]


def test_cancelled_dates_cannot_create_recurrence_from_one_settlement():
    rows = [event("oct", date(2025, 10, 5)), event("nov", date(2025, 11, 5), status="cancelled")]
    f, p, q = model(rows)
    ctx = EvidenceContext(event_patches={"nov": EventPatch("nov", cancel=True)})
    assert not f._series_for_user("u", DAY, ctx)


def test_other_employer_confirmation_cannot_establish_recurrence():
    rows = [salary("a_dec", 12), salary("b_jan", 1, "900", "Employer B", future=True)]
    f, p, q = model(rows)
    assert not f._series_for_user("u", DAY, EvidenceContext())
    assert [(x.flow_date, x.amount, x.source) for x in f.build_cashflows(p, q)] == [
        (date(2026, 1, 15), D("900"), "b_jan")]


def test_same_employer_first_and_confirmed_salary_establish_recurrence():
    rows = [salary("a_dec", 12), salary("a_jan", 1, "900", future=True)]
    f, p, q = model(rows)
    assert [(x.flow_date, x.amount) for x in f.build_cashflows(p, q)] == [
        (date(2026, m, 15), D("900")) for m in (1, 2, 3)]


def test_distinct_same_day_confirmation_preserves_established_salary():
    rows = [salary(f"a_{m}", m) for m in (10, 11, 12)]
    rows.append(salary("b_jan", 1, "900", "Employer B", future=True))
    f, p, q = model(rows)
    january = [x for x in f.build_cashflows(p, q) if x.flow_date.month == 1]
    assert {x.source for x in january} == {"series:a_12", "b_jan"}
    assert sum(x.amount for x in january) == D("1400")


def test_equal_salaries_do_not_override_named_employer_identity():
    rows = [salary(f"{name}_{m}", m, employer=f"Employer {name}")
            for name in ("A", "B") for m in (10, 11, 12)]
    rows.append(salary("b_jan", 1, employer="Employer B", future=True))
    f, p, q = model(list(reversed(rows)))
    january = [x for x in f.build_cashflows(p, q) if x.flow_date.month == 1]
    assert {x.source for x in january} == {"series:A_12", "b_jan"}


def test_ambiguous_confirmation_replaces_only_possible_same_day_overlaps():
    rows = [salary(f"{name}_{m}", m, employer=f"Employer {name}")
            for name in ("A", "B") for m in (10, 11, 12)]
    rows += [salary(f"c_{m}", m, "200", "Employer C", day=20) for m in (10, 11, 12)]
    rows.append(salary("unknown", 1, "800", "Next", future=True))
    f, p, q = model(rows)
    january = [x for x in f.build_cashflows(p, q) if x.flow_date.month == 1]
    assert {x.source for x in january} == {"unknown", "series:c_12"}
    assert sum(x.amount for x in january) == D("1000")
    assert all("unknown" not in s.member_event_ids for s in f._series_for_user("u", DAY, EvidenceContext()))


def test_added_required_debit_cannot_increase_capacity():
    f, p, q = model(balance="1000", amount="1000")
    before = f.max_safe_payment(p, q)
    g, p, q = model([event("bill", date(2026, 1, 20), "200", status="pending")],
                    balance="1000", amount="1000")
    assert g.max_safe_payment(p, q) == before - D("200")


def test_unknown_credit_cannot_increase_capacity_and_one_cent_breach_fails():
    f, p, q = model([event("unknown", DAY, None, direction="credit", category="salary", status="pending")],
                    balance="150", amount="100")
    assert f.max_safe_payment(p, q) == D("50")
    assert f.simulate_plan(p, q, [PaymentLeg(DAY, D("50"))]).safe
    assert not f.simulate_plan(p, q, [PaymentLeg(DAY, D("50.01"))]).safe


def test_other_users_and_input_order_cannot_change_income_association():
    rows = [salary(f"a_{m}", m) for m in (10, 11, 12)] + [salary("next", 1, future=True)]
    f, p, q = model(rows)
    g, _, _ = model(list(reversed(rows)))
    g.dataset.events_by_user["other"] = [replace(salary("outside", 1, "99999", future=True), user_id="other")]
    assert sorted((x.flow_date, x.amount, x.source) for x in f.build_cashflows(p, q)) == sorted(
        (x.flow_date, x.amount, x.source) for x in g.build_cashflows(p, q))


def test_named_notice_can_amend_one_unnamed_payroll_but_not_a_different_employer():
    from buy_or_wait.evidence.interpret import interpret_message
    from buy_or_wait.ingest.loader import MessageRow
    from test_reconstruction import fact
    for description, expected in [("Payroll credit", D("550")), ("Employer A payroll", D("500"))]:
        rows = [replace(salary(f"a_{m}", m), description=description) for m in (10, 11, 12)]
        f, p, q = model(rows)
        raw = fact(subject="Employer B")
        msg = MessageRow("notice", "u", "", "", "2025-12-30T00:00:00Z", "employer", raw["quote"])
        ctx = interpret_message(f.dataset, f.settings, msg, DAY, {"accepted": [raw]})
        assert not ctx.confirmed_flows
        assert [x.amount for x in f.build_cashflows(p, q, evidence=ctx)] == [expected] * 3


def test_linked_new_employer_notice_does_not_amend_established_employer():
    from buy_or_wait.evidence.interpret import interpret_message
    from buy_or_wait.ingest.loader import MessageRow
    from test_reconstruction import fact
    rows = [salary(f"a_{m}", m) for m in (10, 11, 12)]
    rows.append(salary("b_jan", 1, "900", "Employer B", future=True))
    f, p, q = model(rows)
    raw = fact(amount="750", subject="Employer B")
    msg = MessageRow("notice", "u", "", "b_jan", "2025-12-30T00:00:00Z", "employer", raw["quote"])
    ctx = interpret_message(f.dataset, f.settings, msg, DAY, {"accepted": [raw]})
    january = [x for x in f.build_cashflows(p, q, evidence=ctx) if x.flow_date.month == 1]
    assert {x.source: x.amount for x in january} == {"series:a_12": D("500"), "b_jan": D("750")}


@pytest.mark.parametrize("duplicate", [False, True])
def test_accounting_rejects_a_missing_or_duplicated_explicit_obligation(duplicate):
    from buy_or_wait.domain import PlanCandidate
    from buy_or_wait.verification.case_audit import case_audit
    f, p, q = model([event("bill", date(2026, 1, 20), "20", status="pending")])
    actual = f.build_cashflows(p, q)
    f.build_cashflows = lambda *args, **kwargs: actual * 2 if duplicate else []
    engine = SimpleNamespace(dataset=f.dataset, settings=f.settings, forecast=f)
    with pytest.raises(ValueError, match="Explicit cash accounting mismatch"):
        case_audit(engine, q, EvidenceContext(), [], PlanCandidate("not_recommended", [], D("0")))


def test_accounting_rejects_duplicate_recurring_membership():
    from buy_or_wait.domain import PlanCandidate
    from buy_or_wait.verification.case_audit import case_audit
    f, p, q = model([event("nov", date(2025, 11, 5)), event("dec", date(2025, 12, 5))])
    items = f._series_for_user("u", DAY, EvidenceContext())
    f._series_for_user = lambda *args: items * 2
    engine = SimpleNamespace(dataset=f.dataset, settings=f.settings, forecast=f)
    with pytest.raises(ValueError, match="multiple series"):
        case_audit(engine, q, EvidenceContext(), [], PlanCandidate("not_recommended", [], D("0")))
