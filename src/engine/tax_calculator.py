from decimal import Decimal
from src.models.gain_record import GainRecord


class TaxCalculator:
    """
    Computes annual tax summary from a list of GainRecord objects.

    Applies:
    - GVK Article 80 (annual capital gain exemption)
    - GVK Article 81 (progressive income tax brackets)

    All thresholds and brackets are configuration-driven.
    """

    def __init__(self, config: dict) -> None:
        self._config = config
        self._exemption = config["exemptions"]["annual_gain_exemption_tl"]
        self._brackets = config["tax_brackets"]
        self._fiscal_year = config["fiscal_year"]

    def calculate(self, records: list[GainRecord]) -> dict:
        """
        Calculates yearly tax metrics.

        Returns a dictionary containing:
        - total gains
        - total losses
        - net gain
        - exemption applied
        - taxable base
        - estimated tax
        """

        # Decimal-safe summation (prevents int fallback if list is empty)
        total_gain = sum(
            (r.realized_gain_tl for r in records if r.realized_gain_tl > 0),
            Decimal("0"),
        )

        total_loss = sum(
            (r.realized_gain_tl for r in records if r.realized_gain_tl < 0),
            Decimal("0"),
        )

        # Loss values are already negative
        net_gain = total_gain + total_loss

        # Exemption logic (GVK Art. 80 compliant)
        # Negative net gains should NOT trigger exemption application
        if net_gain <= Decimal("0"):
            taxable_base = Decimal("0")
            exemption_applied = Decimal("0")

        elif net_gain <= self._exemption:
            taxable_base = Decimal("0")
            exemption_applied = net_gain

        else:
            taxable_base = net_gain - self._exemption
            exemption_applied = self._exemption

        estimated_tax = self._apply_brackets(taxable_base)

        return {
            "fiscal_year": self._fiscal_year,
            "total_gain_tl": total_gain,
            "total_loss_tl": total_loss,
            "net_gain_tl": net_gain,
            "exemption_applied_tl": exemption_applied,
            "taxable_base_tl": taxable_base,
            "estimated_tax_tl": estimated_tax,
        }

    def _apply_brackets(self, taxable_base: Decimal) -> Decimal:
        """
        Applies progressive income tax brackets.

        Iterates from lowest to highest bracket.
        """

        if taxable_base <= Decimal("0"):
            return Decimal("0")

        total_tax = Decimal("0")
        remaining = taxable_base
        previous_limit = Decimal("0")

        for bracket in self._brackets:
            rate = bracket["rate"]
            upper = bracket["upper_limit_tl"]

            if upper is None:
                # Final bracket (no upper bound)
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