from dataclasses import replace
from datetime import timedelta
from decimal import Decimal as D

from buy_or_wait.evidence.models import EvidenceContext
from buy_or_wait.verification.expense_candidate import calendar_window_estimate, CalendarWindowForecast
from buy_or_wait.verification.horizon_backtest import evaluate_horizons, trajectory_metrics, promotion_check, user_partition
from test_correctness import DAY, event, forecast


def routine_history():
    return [event(str(i), DAY - timedelta(days=7 * i), str(10 + i % 4), category="groceries", description="Grocer")
            for i in range(1, 27)]


def test_calendar_model_uses_complete_windows_and_no_future_observations():
    rows = routine_history()
    f, p, q = forecast(rows)
    series, = f._series_for_user("u", DAY, EvidenceContext())
    amount, audit = calendar_window_estimate(series, rows, DAY)
    assert audit["eligible"]
    assert [(w["occurrences"], w["total"]) for w in audit["windows"]] == [(4, "46"), (4, "46"), (4, "46")]
    assert amount == D("11.50")
    future = event("future", DAY + timedelta(days=1), "999999", category="groceries")
    assert calendar_window_estimate(series, rows + [future], DAY) == (amount, audit)


def test_missing_cycle_prevents_calendar_recalibration():
    rows = routine_history()
    f, p, q = forecast(rows)
    series, = f._series_for_user("u", DAY, EvidenceContext())
    incomplete = [e for e in rows if e.event_id != "2"]
    amount, audit = calendar_window_estimate(series, incomplete, DAY)
    assert amount == series.amount and not audit["eligible"]
    assert "missing" in audit["reason"]


def test_explicit_bill_is_unchanged_by_experimental_estimator():
    rows = routine_history() + [event("bill", DAY + timedelta(days=1), "500", status="scheduled", category="groceries")]
    f, p, q = forecast(rows)
    candidate = CalendarWindowForecast(f.dataset, f.settings)
    series, = candidate._series_for_user("u", DAY, EvidenceContext())
    assert series.estimator == "calendar_window_q75"
    bill, = [c for c in candidate.build_cashflows(p, q) if c.source == "bill"]
    assert bill.amount == D("500")


def test_cumulative_metrics_include_unmatched_expenses_and_drawdown():
    result = trajectory_metrics([D(0), D(70), D(20)], [D(100), D(0), D(0)],
                                [D(0), D(50), D(20)], [D(100), D(0), D(0)])
    assert result["actual_outflow"] == "90"
    assert D(result["maximum_prefix_underprediction_fraction"]) == D(20) / 90
    assert result["actual_maximum_drawdown"] == "90"
    assert result["predicted_maximum_drawdown"] == "70"
    assert D(result["maximum_net_overstatement_fraction"]) == D(20) / 90


def test_historical_validation_cannot_invent_unknown_amounts_or_use_current_balance():
    rows = routine_history() + [event("unknown", DAY - timedelta(days=1), None, category="utilities")]
    f, p, q = forecast(rows)
    first = evaluate_horizons(f.dataset, f.policy)
    assert all(fold["unscorable"] and not fold["models"] for fold in first["folds"])
    assert all(fold["unpredicted_observed_buckets"] for fold in first["folds"])
    f.dataset.profiles["u"] = replace(p, current_available_balance=D("999999"))
    assert evaluate_horizons(f.dataset, f.policy) == first


def test_partition_keeps_public_samples_out_of_model_selection():
    assert user_partition("sample_person", {"sample_person"}) == "public_audit"
    assert user_partition("person", set()) == user_partition("person", {"sample_person"})
    assert user_partition("person", set()) in {"development", "validation"}


def test_lower_average_error_does_not_override_worse_underprediction():
    metrics = dict(mean_absolute_outflow_error_fraction="0.05", mean_outflow_underprediction_fraction="0.01",
                   mean_maximum_prefix_underprediction_fraction="0.01", worst_prefix_underprediction_fraction="0.1",
                   mean_maximum_net_overstatement_fraction="0.01", mean_minimum_cash_overstatement_fraction="0.01",
                   underpredicted_folds=1)
    summary = {"development": {str(h): {"paired_scorable_folds": 10, "folds_with_changed_estimates": 10,
              "models": {"occurrence_q75": dict(metrics), "calendar_window_q75": dict(metrics)}} for h in (30, 60, 90)}}
    for item in summary["development"].values():
        item["models"]["calendar_window_q75"]["mean_absolute_outflow_error_fraction"] = "0.04"
    assert promotion_check(summary, "development")["eligible"]
    summary["development"]["90"]["models"]["calendar_window_q75"]["underpredicted_folds"] = 2
    assert not promotion_check(summary, "development")["eligible"]
