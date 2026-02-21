from decimal import Decimal
from datetime import date
from pathlib import Path

import pandas as pd


class ReferenceDataService:
    """
    In-memory loader for CBRT (TCMB) FX rates and TURKSTAT (TÜİK) WPI indices.
    All values stored as Decimal to ensure financial calculation precision.
    """

    def __init__(self, rates_path: str, wpi_path: str) -> None:
        self._exchange_rates: dict[str, Decimal] = {}
        self._wpi_indices: dict[tuple[int, int], Decimal] = {}

        self._load_rates(rates_path)
        self._load_wpi(wpi_path)

    def _load_rates(self, path: str) -> None:
        df = pd.read_csv(Path(path), dtype=str)
        df.columns = df.columns.str.strip().str.lower()

        for _, row in df.iterrows():
            self._exchange_rates[row["date"].strip()] = Decimal(
                row["usd_try"].strip()
            )

    def _load_wpi(self, path: str) -> None:
        df = pd.read_csv(Path(path), dtype=str)
        df.columns = df.columns.str.strip().str.lower()

        for _, row in df.iterrows():
            key = (int(row["year"]), int(row["month"]))
            self._wpi_indices[key] = Decimal(row["wpi_index"].strip())

    def get_rate(self, trade_date: date, currency: str = "USD") -> Decimal:
        """
        Returns CBRT (TCMB) buying rate for the given date.
        Currently supports USD only — EUR support planned for v1.0.
        """
        key = trade_date.isoformat()
        if key not in self._exchange_rates:
            raise ValueError(
                f"CBRT(TCMB) exchange rate not found. {key}. "
                f"Please check tcmb_rates.csv file."
            )
        return self._exchange_rates[key]

    def get_wpi(self, year: int, month: int) -> Decimal:
        """
        Returns TÜİK WPI index value for the given year and month.
        FIFO engine uses the month preceding the trade date (month - 1).
        """
        key = (year, month)
        if key not in self._wpi_indices:
            raise ValueError(
                f"TURKSTAT(TÜİK) WPI index not found: {year}/{month}. "
                f"Please check tuik_wpi.csv file."
            )
        return self._wpi_indices[key]