"""Paired 30/60/90-day cash-flow validation on historical participant inputs.

Balances are relative to zero, not invented historical bank balances. Public
sample users are a separate audit cohort, excluded from model selection. Final
snapshot statuses and absence of historical evidence limit interpretation.
"""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
import hashlib

from buy_or_wait.finance.recurrence import detect_recurring_series, project_series_dates
from buy_or_wait.verification.expense_candidate import calendar_window_estimate

MODELS = ("occurrence_q75", "calendar_window_q75")


def user_partition(user_id, sample_users):
    if user_id in sample_users:
        return "public_audit"
    # Fixed before any candidate results; never split the same user's history.
    bucket = int(hashlib.sha256(("expense-horizon-v1:" + user_id).encode()).hexdigest(), 16) % 10
    return "validation" if bucket < 3 else "development"


def trajectory_metrics(actual_debits, actual_credits, predicted_debits, predicted_credits):
    size = len(actual_debits)
    if not all(len(values) == size for values in (actual_credits, predicted_debits, predicted_credits)):
        raise ValueError("Mismatched daily horizons")
    actual_total = sum(actual_debits, Decimal(0))
    predicted_total = sum(predicted_debits, Decimal(0))
    actual_expense = predicted_expense = actual_net = predicted_net = Decimal(0)
    actual_peak = predicted_peak = actual_drawdown = predicted_drawdown = Decimal(0)
    actual_min = predicted_min = prefix_under = net_optimism = Decimal(0)
    daily = []
    for i in range(size):
        actual_expense += actual_debits[i]
        predicted_expense += predicted_debits[i]
        actual_net += actual_credits[i] - actual_debits[i]
        predicted_net += predicted_credits[i] - predicted_debits[i]
        actual_peak = max(actual_peak, actual_net)
        predicted_peak = max(predicted_peak, predicted_net)
        actual_drawdown = max(actual_drawdown, actual_peak - actual_net)
        predicted_drawdown = max(predicted_drawdown, predicted_peak - predicted_net)
        actual_min = min(actual_min, actual_net)
        predicted_min = min(predicted_min, predicted_net)
        prefix_under = max(prefix_under, actual_expense - predicted_expense)
        net_optimism = max(net_optimism, predicted_net - actual_net)
        daily.append({"offset": i, "actual_outflow": str(actual_debits[i]), "predicted_outflow": str(predicted_debits[i]),
                      "actual_net_change": str(actual_net), "predicted_net_change": str(predicted_net)})
    def fraction(value):
        return str(value / actual_total) if actual_total > 0 else None
    return {"actual_outflow": str(actual_total), "predicted_outflow": str(predicted_total),
            "absolute_outflow_error_fraction": fraction(abs(predicted_total - actual_total)),
            "outflow_underprediction_fraction": fraction(max(Decimal(0), actual_total - predicted_total)),
            "maximum_prefix_underprediction_fraction": fraction(prefix_under),
            "maximum_net_overstatement_fraction": fraction(net_optimism),
            "actual_minimum_relative_cash": str(actual_min), "predicted_minimum_relative_cash": str(predicted_min),
            "actual_maximum_drawdown": str(actual_drawdown), "predicted_maximum_drawdown": str(predicted_drawdown),
            "minimum_cash_overstatement_fraction": fraction(max(Decimal(0), predicted_min - actual_min)), "daily": daily}


def summarize(folds):
    result = {}
    for split in ("development", "validation", "public_audit"):
        result[split] = {}
        for horizon in (30, 60, 90):
            selected = [f for f in folds if f["split"] == split and f["horizon"] == horizon]
            paired = [f for f in selected if not f["unscorable"] and
                      f["models"][MODELS[0]]["absolute_outflow_error_fraction"] is not None]
            models = {}
            for model in MODELS:
                data = [f["models"][model] for f in paired]
                def average(field):
                    values = [Decimal(d[field]) for d in data]
                    return str(sum(values) / len(values)) if values else None
                models[model] = {
                    "mean_absolute_outflow_error_fraction": average("absolute_outflow_error_fraction"),
                    "mean_outflow_underprediction_fraction": average("outflow_underprediction_fraction"),
                    "mean_maximum_prefix_underprediction_fraction": average("maximum_prefix_underprediction_fraction"),
                    "worst_prefix_underprediction_fraction": str(max((Decimal(d["maximum_prefix_underprediction_fraction"])
                                                                      for d in data), default=Decimal(0))),
                    "mean_maximum_net_overstatement_fraction": average("maximum_net_overstatement_fraction"),
                    "mean_minimum_cash_overstatement_fraction": average("minimum_cash_overstatement_fraction"),
                    "underpredicted_folds": sum(Decimal(d["outflow_underprediction_fraction"]) > 0 for d in data),
                }
            result[split][str(horizon)] = {"folds": len(selected), "paired_scorable_folds": len(paired),
                "folds_with_changed_estimates": sum(any(s["candidate"] != s["control"] for s in f["series"]) for f in paired),
                "unscorable_folds": len(selected) - len(paired), "models": models}
    return result


def promotion_check(summary, split, models=MODELS):
    reasons = []
    improvement = False
    for horizon, result in summary[split].items():
        control, candidate = (result["models"][m] for m in models)
        if not result["paired_scorable_folds"] or not result["folds_with_changed_estimates"]:
            reasons.append(f"{horizon}d: insufficient changed, scorable forecasts")
            continue
        for metric in ("mean_absolute_outflow_error_fraction", "mean_outflow_underprediction_fraction",
                       "mean_maximum_prefix_underprediction_fraction", "worst_prefix_underprediction_fraction",
                       "mean_maximum_net_overstatement_fraction", "mean_minimum_cash_overstatement_fraction",
                       "underpredicted_folds"):
            if Decimal(str(candidate[metric])) > Decimal(str(control[metric])):
                reasons.append(f"{horizon}d: {metric} worsened")
        improvement |= (Decimal(candidate["mean_absolute_outflow_error_fraction"]) <
                        Decimal(control["mean_absolute_outflow_error_fraction"]))
    if not improvement:
        reasons.append("No cumulative expense accuracy improvement")
    return {"eligible": not reasons, "reasons": reasons}


def evaluate_horizons(dataset, policy):
    requests = {q.user_id: q for q in dataset.context_requests_by_id.values()}
    requests.update({q.user_id: q for q in dataset.requests})
    evaluation_users = {q.user_id for q in dataset.requests}
    sample_users = set(requests) - evaluation_users
    rates = {(r.rate_date, r.from_currency, r.to_currency): r.rate for r in dataset.exchange_rates}
    folds = []
    for uid, request in sorted(requests.items()):
        events = dataset.events_by_user[uid]
        home_currency = dataset.profiles[uid].home_currency
        for horizon in (30, 60, 90):
            cutoff = request.request_date - timedelta(days=horizon)
            history = sorted([e for e in events if e.status == "settled" and e.event_date < cutoff
                              and e.settlement_date < cutoff], key=lambda e: (e.settlement_date, e.event_id))
            observed = sorted([e for e in events if e.status == "settled" and e.direction in {"credit", "debit"}
                               and cutoff <= e.settlement_date < request.request_date],
                              key=lambda e: (e.settlement_date, e.event_id))
            unscorable = set()
            def converted(amount, currency, day, source):
                if amount is None:
                    unscorable.add("unknown amount: " + source)
                    return Decimal(0)  # Metrics for the whole fold are withheld below.
                if currency != home_currency:
                    key = (day, currency, home_currency)
                    if key not in rates:
                        unscorable.add("missing dated FX: " + source + " / " + str(day))
                        return Decimal(0)
                    amount = (amount * rates[key]).quantize(Decimal("0.01"))
                return amount
            actual = {d: [Decimal(0)] * horizon for d in ("credit", "debit")}
            predicted = {m: {d: [Decimal(0)] * horizon for d in ("credit", "debit")} for m in MODELS}
            for event in observed:
                actual[event.direction][(event.settlement_date - cutoff).days] += converted(
                    event.amount, event.currency, event.settlement_date, event.event_id)
            descriptions = []
            predicted_keys = set()
            for series in detect_recurring_series(history, cutoff, policy):
                estimate, detail = calendar_window_estimate(series, history, cutoff)
                descriptions.append({"identity": series.series_key, "control": str(series.amount),
                                     "candidate": str(estimate), "evidence": detail,
                                     "members": list(series.member_event_ids)})
                anchor = dataset.events_by_id[series.template_event_id].settlement_date
                for day in project_series_dates(cutoff, request.request_date - timedelta(days=1), series.cadence_days,
                                                anchor, monthly=series.monthly, anchor_day=series.anchor_day):
                    predicted_keys.add((str(day), series.direction, series.category, series.currency))
                    for model, amount in zip(MODELS, (series.amount, estimate)):
                        predicted[model][series.direction][(day - cutoff).days] += converted(
                            amount, series.currency, day, series.series_key)
            observed_keys = {(str(e.settlement_date), e.direction, e.category, e.currency) for e in observed}
            folds.append({"user_id": uid, "split": user_partition(uid, sample_users), "horizon": horizon,
                "cutoff": str(cutoff), "end_exclusive": str(request.request_date), "home_currency": home_currency,
                "history_ids": [e.event_id for e in history], "observed_ids": [e.event_id for e in observed],
                "unpredicted_observed_buckets": [list(k) for k in sorted(observed_keys - predicted_keys)],
                "unobserved_predicted_buckets": [list(k) for k in sorted(predicted_keys - observed_keys)],
                "unscorable": sorted(unscorable), "series": descriptions,
                "models": {m: trajectory_metrics(actual["debit"], actual["credit"], predicted[m]["debit"], predicted[m]["credit"])
                           for m in MODELS} if not unscorable else {}})
    summary = summarize(folds)
    development = promotion_check(summary, "development")
    validation = promotion_check(summary, "validation")
    return {"method": "Historical settled cash movements, including unmatched one-offs; relative cash begins at zero. "
            "No invented historical available balance or forecast FX rates. Unknown amounts make a fold unscorable. "
            "Only pre-cutoff observations train each model; no messages or future confirmations. "
            "Public sample users are excluded from selection; validation users use a fixed SHA-256 partition. "
            "Windows of different lengths overlap and are not independent observations. Final snapshot states limit validity.",
            "candidate_rule": "Upper quartile of three complete 30-day average occurrence costs, at least two "
            "observations and no missing cadence dates in every window; otherwise retain occurrence q75.",
            "selection": {"development": development, "validation": validation,
                          "promote": development["eligible"] and validation["eligible"]},
            "summary": summary, "folds": folds}
