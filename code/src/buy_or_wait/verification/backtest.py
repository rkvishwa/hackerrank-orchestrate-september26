"""Rolling historical validation; no public answers or request-time evidence.

Event state is a final dataset snapshot, not a historical bank snapshot. This
therefore tests recurrence against observed settled history, not historical
decision accuracy. Unknown image amounts stay unknown and are counted separately.
"""
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from buy_or_wait.finance.recurrence import detect_recurring_series, project_series_dates


def historical_backtest(dataset, policy, offsets=(60, 30), window_days=30):
    requests = {q.user_id: q for q in dataset.context_requests_by_id.values()}
    requests.update({q.user_id: q for q in dataset.requests})
    totals = defaultdict(int)
    folds = []
    relative_errors = []
    for uid, request in sorted(requests.items()):
        events = dataset.events_by_user[uid]
        for offset in offsets:
            cutoff = request.request_date - timedelta(days=offset)
            end = cutoff + timedelta(days=window_days - 1)
            history = sorted([e for e in events if e.status == "settled" and e.event_date < cutoff
                              and e.settlement_date < cutoff], key=lambda e: (e.settlement_date, e.event_id))
            held = sorted([e for e in events if e.status == "settled" and e.direction in {"debit", "credit"}
                           and cutoff <= e.settlement_date <= end], key=lambda e: (e.settlement_date, e.event_id))
            predicted = defaultdict(lambda: Decimal(0))
            provenance = defaultdict(list)
            for series in detect_recurring_series(history, cutoff, policy):
                anchor = dataset.events_by_id[series.template_event_id].settlement_date
                for day in project_series_dates(cutoff, end, series.cadence_days, anchor,
                                                monthly=series.monthly, anchor_day=series.anchor_day):
                    key = (day.isoformat(), series.direction, series.category, series.currency)
                    predicted[key] += series.amount
                    provenance[key].append(series.series_key)
            actual = defaultdict(lambda: Decimal(0))
            unknown = set()
            for event in held:
                key = (event.settlement_date.isoformat(), event.direction, event.category, event.currency)
                if event.amount is None:
                    unknown.add(key)
                else:
                    actual[key] += event.amount
            observed_keys = set(actual) | unknown
            matched = set(predicted) & observed_keys
            totals["predicted_date_category_buckets"] += len(predicted)
            totals["observed_date_category_buckets"] += len(observed_keys)
            totals["matched_date_category_buckets"] += len(matched)
            totals["unknown_amount_buckets"] += len(unknown)
            for key in sorted(matched - unknown):
                if actual[key] > 0:
                    relative_errors.append(abs(predicted[key] - actual[key]) / actual[key])
                if key[1] == "debit":
                    totals["matched_debit_buckets"] += 1
                    totals["debit_estimate_covers_observation"] += predicted[key] >= actual[key]
            errors = [{"date": k[0], "direction": k[1], "category": k[2], "currency": k[3],
                       "predicted": str(predicted.get(k, 0)),
                       "observed": None if k in unknown else str(actual.get(k, 0)),
                       "series": provenance.get(k, [])}
                      for k in sorted(set(predicted) ^ observed_keys)]
            folds.append({"user_id": uid, "cutoff": str(cutoff), "end": str(end),
                          "history_ids": [e.event_id for e in history],
                          "held_out_ids": [e.event_id for e in held],
                          "timing_differences": errors})
    totals["folds"] = len(folds)
    totals["users"] = len(requests)
    totals["timing_precision"] = (totals["matched_date_category_buckets"] / totals["predicted_date_category_buckets"]
                                  if totals["predicted_date_category_buckets"] else None)
    totals["timing_recall"] = (totals["matched_date_category_buckets"] / totals["observed_date_category_buckets"]
                               if totals["observed_date_category_buckets"] else None)
    totals["matched_amount_mean_absolute_relative_error"] = (str(sum(relative_errors) / len(relative_errors))
                                                            if relative_errors else None)
    return {"method": "Two historical 30-day windows, starting 60 and 30 days before each request. "
            "Only earlier settled observations train recurrence; no future messages, images, confirmations or sample answers. "
            "Timing uses date/direction/category/native-currency buckets. Unexpected one-offs count as misses. "
            "Amount error covers matched known-amount buckets only. Final snapshot states limit historical validity.",
            "summary": dict(totals), "folds": folds}
