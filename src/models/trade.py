from decimal import Decimal
from datetime import date
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

class TradeType(str, Enum):
    BUY =  "BUY"
    SELL = "SELL"

class Trade(BaseModel):
    trade_id: UUID = Field(default_factory=uuid4)
    ticker: str
    trade_type: TradeType
    quantity: Decimal
    price_fc: Decimal = Field(description="foreign currency(USD)")
    trade_date: date

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_uppercase(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Ticker cannot be empty.")
        return v.upper().strip()

    @field_validator("quantity", "price_fc")
    @classmethod
    def must_be_positive(cls, v: Decimal) ->Decimal:
        if v <= 0:
            raise ValueError("Quantity and price must be greater than zero.")
        return v

    model_config = {
        "frozen": True
} # Trade objects are immutable - cannot be modified after creation.

