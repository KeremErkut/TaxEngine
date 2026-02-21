import pytest
from decimal import Decimal

from src.models.trade import TradeType
from src.engine.fifo_engine import FifoEngine
from tests.conftest import make_trade, make_ref_service, make_config


# -------------------------------------------------------
# TEST 1: Simple full lot match (deterministic gain check)
# -------------------------------------------------------
def test_simple_full_lot_match_exact_gain():
    trades = [
        make_trade("AAPL", TradeType.BUY, 10, 150, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 10, 200, "2024-06-20"),
    ]

    rates = {
        "2024-01-10": Decimal("30"),
        "2024-06-20": Decimal("32"),
    }

    wpi = {
        (2023, 12): Decimal("2800"),
        (2024, 5): Decimal("2900"),
    }

    engine = FifoEngine(make_ref_service(rates, wpi), make_config())
    records = engine.process(trades)

    assert len(records) == 1

    # Deterministic gain calculation:
    # Buy TL = 150 * 30 = 4500
    # Sell TL = 200 * 32 = 6400
    # Gain per share = 1900
    # Total gain = 1900 * 10 = 19000
    expected_gain = Decimal("19000")

    assert records[0].realized_gain_tl == expected_gain


# -------------------------------------------------------
# TEST 2: Negative gain (loss scenario)
# -------------------------------------------------------
def test_loss_scenario_exact():
    trades = [
        make_trade("AAPL", TradeType.BUY, 10, 200, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 10, 150, "2024-06-20"),
    ]

    rates = {
        "2024-01-10": Decimal("30"),
        "2024-06-20": Decimal("30"),
    }

    wpi = {
        (2023, 12): Decimal("2800"),
        (2024, 5): Decimal("2900"),
    }

    engine = FifoEngine(make_ref_service(rates, wpi), make_config())
    records = engine.process(trades)

    # Buy TL = 6000
    # Sell TL = 4500
    # Loss = -1500 per share → -15000 total
    expected_loss = Decimal("-15000")

    assert records[0].realized_gain_tl == expected_loss


# -------------------------------------------------------
# TEST 3: Engine stateless behavior (idempotency)
# -------------------------------------------------------
def test_engine_is_stateless_between_runs():
    trades = [
        make_trade("AAPL", TradeType.BUY, 5, 100, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 5, 200, "2024-06-20"),
    ]

    rates = {
        "2024-01-10": Decimal("30"),
        "2024-06-20": Decimal("30"),
    }

    wpi = {
        (2023, 12): Decimal("2800"),  
        (2024, 5): Decimal("2900"),       
    }

    engine = FifoEngine(make_ref_service(rates, wpi), make_config())

    result_1 = engine.process(trades)
    result_2 = engine.process(trades)

    assert result_1 == result_2


# -------------------------------------------------------
# TEST 4: Cross-ticker isolation
# -------------------------------------------------------
def test_cross_ticker_isolation():
    trades = [
        make_trade("AAPL", TradeType.BUY, 5, 100, "2024-01-10"),
        make_trade("TSLA", TradeType.BUY, 5, 100, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 5, 200, "2024-06-20"),
    ]

    rates = {
        "2024-01-10": Decimal("30"),
        "2024-06-20": Decimal("30"),
    }

    wpi = {
        (2023, 12): Decimal("2800"),  
        (2024, 5): Decimal("2900"),       
    }


    engine = FifoEngine(make_ref_service(rates, wpi), make_config())
    records = engine.process(trades)

    assert len(records) == 1
    assert records[0].ticker == "AAPL"


# -------------------------------------------------------
# TEST 5: Missing FX rate should raise error
# -------------------------------------------------------
def test_missing_fx_rate_raises_error():
    trades = [
        make_trade("AAPL", TradeType.BUY, 10, 150, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 10, 200, "2024-06-20"),
    ]

    # SELL rate missing intentionally
    rates = {
        "2024-01-10": Decimal("30"),
    }

    engine = FifoEngine(make_ref_service(rates, {}), make_config())

    with pytest.raises(ValueError):
        engine.process(trades)


# -------------------------------------------------------
# TEST 6: Exact WPI threshold boundary (1.10)
# -------------------------------------------------------
def test_indexing_exact_threshold_boundary():
    trades = [
        make_trade("AAPL", TradeType.BUY, 10, 150, "2024-01-10"),
        make_trade("AAPL", TradeType.SELL, 10, 200, "2024-06-20"),
    ]

    rates = {
        "2024-01-10": Decimal("30"),
        "2024-06-20": Decimal("30"),
    }

    # Exactly 10% increase
    wpi = {
        (2023, 12): Decimal("2800"),
        (2024, 5): Decimal("3080"),  # 1.10 ratio
    }

    engine = FifoEngine(make_ref_service(rates, wpi), make_config())
    records = engine.process(trades)

    assert records[0].is_indexed is True


# -------------------------------------------------------
# TEST 7: Sell without lot should raise error
# -------------------------------------------------------
def test_sell_without_lot_raises_error():
    trades = [
        make_trade("AAPL", TradeType.SELL, 10, 200, "2024-06-20"),
    ]

    rates = {"2024-06-20": Decimal("30")}

    engine = FifoEngine(make_ref_service(rates, {}), make_config())

    with pytest.raises(ValueError):
        engine.process(trades)