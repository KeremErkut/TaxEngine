from decimal import Decimal
from pathlib import Path
from typing import Any
import yaml


def _to_decimal_if_numeric(value: Any) -> Any:
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    return value


def load_tax_config(path: str = "config/tax_config_2025.yaml") -> dict:
    with open(Path(path), "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # Indexing threshold
    raw["indexing"]["wpi_threshold"] = Decimal(
        str(raw["indexing"]["wpi_threshold"])
    )

    # Exemption
    raw["exemptions"]["annual_gain_exemption_tl"] = Decimal(
        str(raw["exemptions"]["annual_gain_exemption_tl"])
    )

    # Tax brackets
    for bracket in raw["tax_brackets"]:
        bracket["rate"] = Decimal(str(bracket["rate"]))
        if bracket["upper_limit_tl"] is not None:
            bracket["upper_limit_tl"] = Decimal(
                str(bracket["upper_limit_tl"])
            )

    return raw