from decimal import Decimal
from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

class FifoLot(BaseModel):
    lot_id: UUID = Field(default_factory=uuid4)
    purchase_trade_id: UUID = Field(default_factory=uuid4)
    ticker: str
    original_qty: Decimal
    remaining_qty: Decimal
    cost_basis_tl: Decimal # Total cost in TL 
    purchase_date: date

    @field_validator("original_qty", "cost_basis_tl")
    @classmethod
    def must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Quantity and Cost must be greater than zero.")
        return v
    
    @model_validator(mode="after")
    def remaining_cannot_exceed_original(self) -> "FifoLot":
        if self.remaining_qty < 0:
            raise ValueError("The remaining amount cannot exceed the initial amount.")
        if self.remaining_qty > self.original_qty:
            raise ValueError("Remaining cannot exceed original quantity.")
        return self
    
    def is_depleted(self) -> bool:
        return self.remaining_qty <= Decimal("0")
    
    def consume(self, qty: Decimal) -> "FifoLot":
        if qty <= 0:
            raise ValueError("Consume quantity must be positive")
        if qty > self.remaining_qty:
            raise ValueError(
                f"There are not enough shares in the lot."
                f"Demand={qty}, Available={self.remaining_qty}"
            )
        return self.model_copy(update={"remaining_qty": self.remaining_qty - qty})
    
    model_config = {
        "frozen": True # consume() returns a new object, the existing one remains unchanged.
    }
