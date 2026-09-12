from __future__ import annotations

from datetime import date
from decimal import Decimal

from buy_or_wait.ingest.loader import ExchangeRate


class CurrencyConverter:
    def __init__(self, rates: list[ExchangeRate]):
        self._direct: dict[tuple[date, str, str], Decimal] = {}
        for rate in rates:
            self._direct[(rate.rate_date, rate.from_currency, rate.to_currency)] = rate.rate

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, settlement_date: date) -> Decimal:
        if from_currency == to_currency:
            return amount
        rate = self._lookup_rate(from_currency, to_currency, settlement_date)
        return (amount * rate).quantize(Decimal("0.01"))

    def _lookup_rate(self, from_currency: str, to_currency: str, settlement_date: date) -> Decimal:
        direct = self._find_direct(from_currency, to_currency, settlement_date)
        if direct is not None:
            return direct
        for bridge in ("USD", "EUR"):
            if bridge in (from_currency, to_currency):
                continue
            first = self._find_direct(from_currency, bridge, settlement_date)
            second = self._find_direct(bridge, to_currency, settlement_date)
            if first is not None and second is not None:
                return first * second
        if from_currency != "USD" and to_currency != "USD":
            first = self._find_direct(from_currency, "USD", settlement_date)
            second = self._find_direct("USD", to_currency, settlement_date)
            if first is not None and second is not None:
                return first * second
        if from_currency != "EUR" and to_currency != "EUR":
            first = self._find_direct(from_currency, "EUR", settlement_date)
            second = self._find_direct("EUR", to_currency, settlement_date)
            if first is not None and second is not None:
                return first * second
        raise ValueError(f"No exchange rate for {from_currency}->{to_currency} on {settlement_date}")

    def _find_direct(self, from_currency: str, to_currency: str, settlement_date: date) -> Decimal | None:
        exact = self._direct.get((settlement_date, from_currency, to_currency))
        if exact is not None:
            return exact
        candidates = [
            (rate_date, rate)
            for (rate_date, src, dst), rate in self._direct.items()
            if src == from_currency and dst == to_currency and rate_date <= settlement_date
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]
