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
    mock = MagicMock()

    def get_rate(d, currency="USD"):
        key = d.isoformat()
        if key not in rates:
            raise ValueError(f"TCMB kuru bulunamadı: {key}")
        return rates[key]

    def get_wpi(y, m):
        key = (y, m)
        if key not in wpi:
            raise ValueError(f"WPI bulunamadı: {y}/{m}")
        return wpi[key]

    mock.get_rate.side_effect = get_rate
    mock.get_wpi.side_effect = get_wpi
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