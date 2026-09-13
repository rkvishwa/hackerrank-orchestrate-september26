from dataclasses import replace
from datetime import timedelta
from decimal import Decimal as D
import importlib.util
import json
from pathlib import Path

from buy_or_wait.evidence.models import EvidenceContext
from buy_or_wait.verification.source_ledger import daily_ledger, reconstruct_reviewed_case
from buy_or_wait.verification.backtest import historical_backtest
from test_correctness import DAY, event, forecast


def test_alternating_merchants_do_not_halve_recurring_spending():
    # Nine consecutive fortnightly purchases, a favourite every other cycle.
    names = ["Bakery", "Takeaway", "Coffee shop", "Takeaway", "Lunch", "Takeaway", "Snacks", "Restaurant", "Dinner"]
    rows = [event(str(i), DAY - timedelta(days=14 * (9 - i)), "20",
                  category="dining", description=name) for i, name in enumerate(names)]
    f, p, q = forecast(rows)
    s, = f._series_for_user("u", DAY, EvidenceContext())
    assert s.cadence_days == 14 and not s.monthly
    assert set(s.member_event_ids) == {e.event_id for e in rows}
    assert [c.flow_date for c in f.build_cashflows(p, q)] == [DAY + timedelta(days=i) for i in range(0, 90, 14)]


def test_independent_replay_counts_same_day_salary_before_payment():
    flows = [dict(date=str(DAY), amount="500", direction="credit", category="salary", source="pay"),
             dict(date=str(DAY + timedelta(days=1)), amount="250", direction="debit", category="rent", source="rent")]
    result = daily_ledger(D("200"), D("100"), DAY, flows, D("1000"))
    assert D(result["amount_safe"]) == D("350")
    assert result["earliest_full"] == ""


def test_regular_dates_do_not_make_an_exceptional_basket_recurring():
    rows = [event(str(i), DAY - timedelta(days=7 * i), "20", category="groceries",
                  description="Grocer") for i in range(2, 6)]
    rows.append(event("bulk", DAY - timedelta(days=7), "500", category="groceries", description="Bulk pantry shop"))
    f, p, q = forecast(rows)
    s, = f._series_for_user("u", DAY, EvidenceContext())
    assert "bulk" not in s.member_event_ids
    assert s.amount == D("20")


def test_unquantified_commitment_explanation_reaches_output(monkeypatch):
    from buy_or_wait.engine import DecisionEngine
    f, p, q = forecast()
    engine = DecisionEngine(f.dataset, f.settings)
    context = EvidenceContext(unresolved_mandatory_debits={"childcare_notice"})
    monkeypatch.setattr(engine.evidence, "resolve", lambda request: context)
    result = engine.decide(q)
    assert result.amount_safe_to_pay == 0
    assert "no supplied amount or usable payment date" in result.decision_explanation
    assert "childcare_notice" in result.decision_explanation


def test_backtest_cannot_use_future_salary_confirmation():
    rows = [event("past", DAY - timedelta(days=75), "500", category="salary", direction="credit"),
            event("future", DAY + timedelta(days=14), "900", category="salary", direction="credit",
                  status="scheduled", description="Next confirmed salary")]
    f, p, q = forecast(rows)
    before = historical_backtest(f.dataset, f.policy)
    f.dataset.events_by_user["u"][1] = replace(rows[1], amount=D("900000"))
    assert historical_backtest(f.dataset, f.policy) == before
    assert all("future" not in fold["history_ids"] for fold in before["folds"])


def test_reviewed_ledgers_match_engine_without_engine_reconstruction():
    code_root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("diagnose_forecasts", code_root / "scripts/diagnose_forecasts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    settings = module.Settings(_env_file=None, deterministic_mode=True, llm_enabled=False,
                               evidence_cache_dir=code_root / "evaluation/evidence_cache")
    dataset_dir = settings.resolved_dataset_dir
    dataset = module.load_dataset(dataset_dir)
    engine = module.DecisionEngine(dataset, settings)
    cases = json.loads((code_root / "evaluation/reviewed_cases.json").read_text())
    for case in cases:
        reviewed = reconstruct_reviewed_case(dataset_dir, case)
        comparison = module.compare_ledger(reviewed, engine, dataset.context_requests_by_id[case["request_id"]])
        assert comparison["first_ledger_difference"] is None
        assert comparison["capacity_agrees"]
        assert len(reviewed["daily"]) == 90
