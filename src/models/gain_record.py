from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

class GainRecord(BaseModel):
    gain_id: UUID = Field(default_factory=uuid4)
    sell_trade_id: UUID = Field(default_factory=uuid4)
    ticker: str
    matched_qty: Decimal
    realized_gain_tl: Decimal # Positive = Profit, Negative = Loss
    is_indexed: bool
    audit_note: str = "" # Like "WPI: 1.12 >= 1.10, indexing applied"

    @field_validator("matched_qty")
    @classmethod
    def quantity_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Matched quantity must be positive.")
        return v
    
    model_config = {
        "frozen": True
    }