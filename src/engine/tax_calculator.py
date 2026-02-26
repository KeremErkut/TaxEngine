from decimal import Decimal
from src.models.gain_record import GainRecord


class TaxCalculator:
    """
    Computes annual tax summary from a list of GainRecord objects.

    Applies:
    - GVK Mük. Madde 81 (WPI indexing + progressive income tax brackets)

    Note: No exemption or declaration threshold applies to foreign equity
    capital gains. All net gains are fully taxable regardless of amount.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._brackets = config["tax_brackets"]
        self._fiscal_year = config["fiscal_year"]

    def calculate(self, records: list[GainRecord]) -> dict:

        total_gain = sum(
            (r.realized_gain_tl for r in records if r.realized_gain_tl > 0),
            Decimal("0"),
        )

        total_loss = sum(
            (r.realized_gain_tl for r in records if r.realized_gain_tl < 0),
            Decimal("0"),
        )

        net_gain = total_gain + total_loss

        # No exemption for foreign equity capital gains (GVK Mük. 81)
        taxable_base = max(net_gain, Decimal("0"))

        estimated_tax = self._apply_brackets(taxable_base)

        return {
            "fiscal_year": self._fiscal_year,
            "total_gain_tl": total_gain,
            "total_loss_tl": total_loss,
            "net_gain_tl": net_gain,
            "taxable_base_tl": taxable_base,
            "estimated_tax_tl": estimated_tax,
        }

    def _apply_brackets(self, taxable_base: Decimal) -> Decimal:
        if taxable_base <= Decimal("0"):
            return Decimal("0")

        total_tax = Decimal("0")
        remaining = taxable_base
        previous_limit = Decimal("0")

        for bracket in self._brackets:
            rate = bracket["rate"]
            upper = bracket["upper_limit_tl"]

            if upper is None:
                total_tax += remaining * rate
                break

            bracket_size = upper - previous_limit

            if remaining <= bracket_size:
                total_tax += remaining * rate
                break
            else:
                total_tax += bracket_size * rate
                remaining -= bracket_size
                previous_limit = upper

        return total_tax