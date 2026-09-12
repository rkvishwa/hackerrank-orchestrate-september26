from __future__ import annotations

from datetime import date
from decimal import Decimal
from buy_or_wait.ingest.loader import ExchangeRate


class CurrencyConverter:
    """Use only the supplied settlement-date rate in the stated direction."""
    def __init__(self, rates: list[ExchangeRate]):
        self._direct = {(r.rate_date, r.from_currency, r.to_currency): r.rate for r in rates}

    def convert(self, amount: Decimal, from_currency: str, to_currency: str, settlement_date: date) -> Decimal:
        if from_currency == to_currency:
            return amount
        key = (settlement_date, from_currency, to_currency)
        if key not in self._direct:
            raise ValueError(f"No exact exchange rate for {from_currency}->{to_currency} on {settlement_date}")
        return (amount * self._direct[key]).quantize(Decimal("0.01"))
