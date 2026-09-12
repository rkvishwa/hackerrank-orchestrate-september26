"""Evaluation-only reconstruction from reviewed rules and original CSV records.

No imports from the financial engine, recurrence detector, evidence interpreter,
or capacity verifier. Reviewed rules specify membership and cadence, never an
answer or an estimated amount. This is a second calculation, not a second
implementation of automatic evidence interpretation.
"""
from __future__ import annotations

import calendar
import csv
import hashlib
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_CEILING


def read_rows(directory, name):
    with (directory / (name + ".csv")).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def daily_ledger(opening, reserve, start, flows, requested, horizon=90):
    """Brute-force every possible full-payment day; no suffix/binary search."""
    by_day = defaultdict(list)
    for flow in flows:
        day = date.fromisoformat(flow["date"])
        if not start <= day < start + timedelta(days=horizon):
            raise ValueError("Reviewed flow outside forecast")
        by_day[day].append(flow)
    balance = opening
    daily = []
    transactions = []
    for offset in range(horizon):
        day = start + timedelta(days=offset)
        for flow in sorted(by_day[day], key=lambda f: (f["direction"] != "credit", f["source"])):
            balance += Decimal(flow["amount"]) * (1 if flow["direction"] == "credit" else -1)
            transactions.append({**flow, "balance_after": str(balance)})
        daily.append({"date": day.isoformat(), "balance": str(balance), "headroom": str(balance - reserve)})
    minimum = min([opening, *(Decimal(d["balance"]) for d in daily)])
    capacity = (min(requested, max(Decimal(0), min(Decimal(d["balance"]) for d in daily) - reserve))
                if minimum >= reserve else Decimal(0))
    earliest = None
    if minimum >= reserve:
        for offset in range(horizon):
            if all(Decimal(row["balance"]) - requested >= reserve for row in daily[offset:]):
                earliest = daily[offset]["date"]
                break
    return {"amount_safe": str(capacity), "earliest_full": earliest or "",
            "minimum_balance": str(minimum), "daily": daily, "transactions": transactions}


def reconstruct_reviewed_case(directory, specification):
    # Explicitly discard public output columns at the input boundary.
    fields = ("request_id", "user_id", "request_date", "requested_amount", "desired_completion_date")
    requests = read_rows(directory, "requests") + read_rows(directory, "sample_requests")
    raw = next(r for r in requests if r["request_id"] == specification["request_id"])
    request = {key: raw[key] for key in fields}
    user = request["user_id"]
    profile = next(r for r in read_rows(directory, "financial_profiles") if r["user_id"] == user)
    events = [r for r in read_rows(directory, "financial_events") if r["user_id"] == user]
    messages = [r for r in read_rows(directory, "messages") if r["user_id"] == user]
    images = [r for r in read_rows(directory, "images") if r["user_id"] == user]
    if {r["message_id"] for r in messages} != set(specification.get("reviewed_messages", {})) or images:
        raise ValueError("New evidence requires independent review")
    for message in messages:
        digest = hashlib.sha256(message["message_text"].encode("utf-8")).hexdigest()
        if digest != specification.get("message_sha256", {}).get(message["message_id"]):
            raise ValueError("Changed message requires independent review")
    rates = {(r["rate_date"], r["from_currency"], r["to_currency"]): Decimal(r["rate"])
             for r in read_rows(directory, "exchange_rates")}
    start = date.fromisoformat(request["request_date"])
    end = start + timedelta(days=89)
    historical = [r for r in events if r["status"] == "settled" and r["settlement_date"] < str(start)]
    series = []
    membership = {}
    for rule in specification["series"]:
        members = sorted([r for r in historical if all(r[k] == v for k, v in rule["match"].items())],
                         key=lambda r: (r["settlement_date"], r["event_id"]))
        if len(members) < 2 or any(r["amount"] == "" for r in members):
            raise ValueError("Insufficient reviewed series observations")
        for row in members:
            if row["event_id"] in membership:
                raise ValueError("Overlapping reviewed series")
            membership[row["event_id"]] = rule["name"]
        if len({r["currency"] for r in members}) != 1:
            raise ValueError("Review currencies independently")
        cycle_amounts = defaultdict(lambda: Decimal(0))
        for row in members:
            cycle_amounts[row["settlement_date"]] += Decimal(row["amount"])
        dates = [date.fromisoformat(day) for day in sorted(cycle_amounts)]
        if "monthly_day" in rule:
            if any(d.day != min(rule["monthly_day"], calendar.monthrange(d.year, d.month)[1]) for d in dates):
                raise ValueError("Reviewed monthly cadence contradicted by history")
        elif any((b - a).days != rule["interval_days"] for a, b in zip(dates, dates[1:])):
            raise ValueError("Reviewed interval contradicted by history")
        recent = [cycle_amounts[str(d)] for d in dates[-12:]]
        if members[0]["direction"] == "credit":
            if len(set(recent)) != 1:
                raise ValueError("Variable income requires separate review")
            amount = recent[-1]
        else:
            rank = int((Decimal("0.75") * len(recent)).to_integral_value(rounding=ROUND_CEILING))
            amount = sorted(recent)[rank - 1]
        series.append({**rule, "amount": str(amount), "currency": members[0]["currency"],
                       "direction": members[0]["direction"], "category": members[0]["category"],
                       "anchor": str(dates[-1]), "members": [r["event_id"] for r in members],
                       "observations": [str(a) for a in recent]})
    exclusions = []
    for row in historical:
        if row["event_id"] not in membership:
            reason = specification.get("excluded_history", {}).get(row["description"])
            if not reason:
                raise ValueError("Unreviewed history: " + row["event_id"])
            exclusions.append({"event_id": row["event_id"], "reason": reason})
    flows = []
    replaced = set()

    def append(day, amount, currency, direction, category, source):
        if currency != profile["home_currency"]:
            amount = (amount * rates[(str(day), currency, profile["home_currency"])]).quantize(Decimal("0.01"))
        flows.append(dict(date=str(day), amount=str(amount), direction=direction, category=category, source=source))

    for row in events:
        if row in historical:
            continue
        if row["status"] in {"failed", "cancelled", "unrealized"} or row["direction"] == "non_cash":
            exclusions.append({"event_id": row["event_id"], "reason": "No settled or outstanding cash movement"})
            continue
        if row["direction"] == "credit" and row["status"] != "settled" and not (
                row["status"] == "scheduled" and "confirmed salary" in row["description"].lower()):
            exclusions.append({"event_id": row["event_id"], "reason": "Unconfirmed credit"})
            continue
        day = max(start, date.fromisoformat(row["settlement_date"]))
        if day > end:
            exclusions.append({"event_id": row["event_id"], "reason": "Outside horizon"})
            continue
        append(day, Decimal(row["amount"]), row["currency"], row["direction"], row["category"], row["event_id"])
        if row["event_id"] in specification.get("replaces_series", {}):
            name = specification["replaces_series"][row["event_id"]]
            target = next(s for s in series if s["name"] == name)
            if target["currency"] != row["currency"] or Decimal(target["amount"]) != Decimal(row["amount"]):
                raise ValueError("Reviewed replacement amount/currency changed")
            replaced.add((str(day), name))
    for item in series:
        anchor = date.fromisoformat(item["anchor"])
        for offset in range(90):
            day = start + timedelta(days=offset)
            due = (day.day == min(item["monthly_day"], calendar.monthrange(day.year, day.month)[1])
                   if "monthly_day" in item else (day - anchor).days % item["interval_days"] == 0)
            if due and (str(day), item["name"]) not in replaced:
                append(day, Decimal(item["amount"]), item["currency"], item["direction"], item["category"], item["name"])
    calculation = daily_ledger(Decimal(profile["current_available_balance"]), Decimal(profile["minimum_balance_to_keep"]),
                               start, flows, Decimal(request["requested_amount"]))
    return {"request": request, "profile": profile, "series": series, "exclusions": exclusions,
            "reviewed_messages": specification.get("reviewed_messages", {}),
            "source_event_count": len(events), "historical_settled_count": len(historical), **calculation}
