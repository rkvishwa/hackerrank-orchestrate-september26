"""Independent baseline oracle using daily balances and suffix minima.

This does not call the simulator or either of the engine's binary searches.
It verifies arithmetic against the same evidence-derived cash-flow ledger.
"""
from datetime import timedelta
from decimal import Decimal, ROUND_FLOOR


def baseline_capacity(profile, request, flows, horizon_days):
    deltas = [Decimal("0") for _ in range(horizon_days)]
    for flow in flows:
        index = (flow.flow_date - request.request_date).days
        if not 0 <= index < horizon_days:
            raise ValueError("Cash flow outside baseline forecast horizon")
        deltas[index] += flow.amount if flow.direction == "credit" else -flow.amount
    balance = profile.current_available_balance
    balances = []
    for delta in deltas:
        balance += delta
        balances.append(balance)
    minimum = min([profile.current_available_balance, *balances])
    if minimum < profile.minimum_balance_to_keep:
        return Decimal("0"), None
    suffix = list(balances)
    for index in range(len(suffix) - 2, -1, -1):
        suffix[index] = min(suffix[index], suffix[index + 1])
    capacities = [max(Decimal("0"), value - profile.minimum_balance_to_keep) for value in suffix]
    amount = min(request.requested_amount, capacities[0]).quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
    earliest = next((request.request_date + timedelta(days=index)
                     for index, value in enumerate(capacities) if value >= request.requested_amount), None)
    return amount, earliest
