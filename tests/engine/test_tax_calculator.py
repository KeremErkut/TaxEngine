import pytest
from decimal import Decimal

from src.engine.tax_calculator import TaxCalculator
from src.models.gain_record import GainRecord
import uuid


def make_gain_record(realized_gain_tl, ticker="AAPL", matched_qty="10", is_indexed=False):
    return GainRecord(
        sell_trade_id=uuid.uuid4(),
        ticker=ticker,
        matched_qty=Decimal(matched_qty),
        realized_gain_tl=Decimal(str(realized_gain_tl)),
        is_indexed=is_indexed,
        wpi_ratio=Decimal("1.05"),
    )


def make_config():
    return {
        "fiscal_year": 2025,
        "tax_brackets": [
            {"upper_limit_tl": Decimal("158000"), "rate": Decimal("0.15")},
            {"upper_limit_tl": Decimal("330000"), "rate": Decimal("0.20")},
            {"upper_limit_tl": Decimal("800000"), "rate": Decimal("0.27")},
            {"upper_limit_tl": Decimal("4300000"), "rate": Decimal("0.35")},
            {"upper_limit_tl": None, "rate": Decimal("0.40")},
        ],
    }


# -------------------------------------------------------
# TEST 1: Net loss — tax must be zero
# -------------------------------------------------------
def test_net_loss_no_tax():
    records = [
        make_gain_record("-50000"),
        make_gain_record("10000"),
    ]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    assert summary["net_gain_tl"] == Decimal("-40000")
    assert summary["taxable_base_tl"] == Decimal("0")
    assert summary["estimated_tax_tl"] == Decimal("0")


# -------------------------------------------------------
# TEST 2: First bracket exact boundary
# -------------------------------------------------------
def test_first_bracket_exact_boundary():
    records = [make_gain_record("158000")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    # 158000 * 0.15
    assert summary["estimated_tax_tl"] == Decimal("23700")


# -------------------------------------------------------
# TEST 3: First bracket + 1 TL
# -------------------------------------------------------
def test_first_bracket_plus_one():
    records = [make_gain_record("158001")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    # 158000 * 0.15 = 23700
    # 1 * 0.20 = 0.20
    expected = Decimal("23700") + Decimal("0.20")
    assert summary["estimated_tax_tl"] == expected


# -------------------------------------------------------
# TEST 4: Progressive bracket multi-tier
# -------------------------------------------------------
def test_progressive_bracket_calculation():
    records = [make_gain_record("340000")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    # 158000 * 0.15 = 23700
    # (330000 - 158000) * 0.20 = 34400
    # (340000 - 330000) * 0.27 = 2700
    assert summary["estimated_tax_tl"] == Decimal("60800")


# -------------------------------------------------------
# TEST 5: Large income — 40% bracket
# -------------------------------------------------------
def test_top_bracket_application():
    records = [make_gain_record("5000000")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    assert summary["taxable_base_tl"] == Decimal("5000000")
    assert summary["estimated_tax_tl"] > Decimal("0")


# -------------------------------------------------------
# TEST 6: Decimal rounding behavior
# -------------------------------------------------------
def test_decimal_rounding_behavior():
    records = [make_gain_record("0.55")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    assert summary["taxable_base_tl"] == Decimal("0.55")


# -------------------------------------------------------
# TEST 7: Taxable base never negative
# -------------------------------------------------------
def test_taxable_base_never_negative():
    records = [make_gain_record("10000")]

    calc = TaxCalculator(make_config())
    summary = calc.calculate(records)

    assert summary["taxable_base_tl"] >= Decimal("0")


# -------------------------------------------------------
# TEST 8: Idempotency — repeated calculation same result
# -------------------------------------------------------
def test_calculator_is_stateless():
    records = [make_gain_record("68000")]

    calc = TaxCalculator(make_config())

    result_1 = calc.calculate(records)
    result_2 = calc.calculate(records)

    assert result_1 == result_2


# -------------------------------------------------------
# TEST 9: Empty records
# -------------------------------------------------------
def test_empty_records():
    calc = TaxCalculator(make_config())
    summary = calc.calculate([])

    assert summary["total_gain_tl"] == Decimal("0")
    assert summary["total_loss_tl"] == Decimal("0")
    assert summary["net_gain_tl"] == Decimal("0")
    assert summary["taxable_base_tl"] == Decimal("0")
    assert summary["estimated_tax_tl"] == Decimal("0")


# -------------------------------------------------------
# TEST 10: Fiscal year from config
# -------------------------------------------------------
def test_fiscal_year_from_config():
    calc = TaxCalculator(make_config())
    summary = calc.calculate([])

    assert summary["fiscal_year"] == 2025