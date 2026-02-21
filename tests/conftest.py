import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock

from src.models.trade import Trade, TradeType


def make_trade(ticker, trade_type, qty, price, trade_date):
    return Trade(
        ticker=ticker,
        trade_type=trade_type,
        quantity=Decimal(str(qty)),
        price_fc=Decimal(str(price)),
        trade_date=date.fromisoformat(trade_date),
    )


def make_ref_service(rates: dict, wpi: dict):
    """
    Creates a mock ReferenceDataService.
    rates: {"YYYY-MM-DD": Decimal}
    wpi:   {(year, month): Decimal}
    """
    mock = MagicMock()
    mock.get_rate.side_effect = lambda d, currency="USD": rates[d.isoformat()]
    mock.get_wpi.side_effect = lambda y, m: wpi[(y, m)]
    return mock


def make_config(wpi_threshold="0.10"):
    return {
        "indexing": {"wpi_threshold": Decimal(wpi_threshold)},
    }


@pytest.fixture
def base_rates():
    return {
        "2024-01-10": Decimal("30"),
        "2024-03-01": Decimal("31"),
        "2024-06-20": Decimal("32"),
    }


@pytest.fixture
def base_wpi():
    return {
        (2023, 12): Decimal("2800"),
        (2024, 2): Decimal("2850"),
        (2024, 5): Decimal("2900"),
    }