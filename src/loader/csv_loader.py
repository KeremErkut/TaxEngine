from decimal import Decimal
from datetime import date
from pathlib import Path

import pandas as pd

from src.loader.base import DataSource
from src.models.trade import Trade, TradeType


REQUIRED_COLUMNS = {
    "trade_date",
    "ticker",
    "trade_type",
    "quantity",
    "price_fc",
    "currency",
}


class CSVLoader(DataSource):
    """
    Loads trade history from CSV or Excel files.
    Maps columns directly to Trade model fields.
    """

    def load(self, source: str) -> list[Trade]:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        # Read according to CSV or Excel
        if path.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(path, dtype=str)
        elif path.suffix.lower() == ".csv":
            df = pd.read_csv(path, dtype=str)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Mandatory column control
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        trades = []
        errors = []

        for idx, row in df.iterrows():  # iterrows fix
            try:
                trade = Trade(
                    ticker=str(row["ticker"]).strip(),
                    trade_type=TradeType(str(row["trade_type"]).strip().upper()),
                    quantity=Decimal(str(row["quantity"]).strip()),
                    price_fc=Decimal(str(row["price_fc"]).strip()),
                    trade_date=date.fromisoformat(str(row["trade_date"]).strip()),
                    currency=str(row["currency"]).strip(),
                )
                trades.append(trade)

            except Exception as e:
                errors.append(f"Row {idx + 2}: {e}")

        if errors:
            error_summary = "\n".join(errors)
            raise ValueError(f"Data errors detected:\n{error_summary}")

        # Chronological order - Mandatory for FIFO engine
        trades.sort(key=lambda t: t.trade_date)

        return trades