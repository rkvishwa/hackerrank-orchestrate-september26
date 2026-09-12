from datetime import date
from decimal import Decimal
import pytest
from buy_or_wait.finance.currency import CurrencyConverter
from buy_or_wait.ingest.loader import ExchangeRate


def test_exact_date_and_direction_required():
    converter = CurrencyConverter([ExchangeRate(date(2026, 1, 1), "USD", "INR", Decimal("80"))])
    assert converter.convert(Decimal("10"), "USD", "INR", date(2026, 1, 1)) == Decimal("800")
    with pytest.raises(ValueError, match="exact exchange rate"):
        converter.convert(Decimal("10"), "USD", "INR", date(2026, 1, 2))
    with pytest.raises(ValueError, match="exact exchange rate"):
        converter.convert(Decimal("800"), "INR", "USD", date(2026, 1, 1))
