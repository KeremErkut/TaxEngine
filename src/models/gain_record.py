from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class GainRecord(BaseModel):
    """
    Immutable domain model representing a realized gain/loss record.

    IMPORTANT:
    - This model contains only structured, machine-readable financial data.
    - No presentation parsing should be required.
    - WPI ratio is stored separately to avoid fragile string parsing.
    """

    gain_id: UUID = Field(default_factory=uuid4)
    sell_trade_id: UUID = Field(default_factory=uuid4)

    ticker: str

    matched_qty: Decimal

    # Positive = Profit, Negative = Loss
    realized_gain_tl: Decimal

    # Indicates whether inflation indexing was applied
    is_indexed: bool

    # NEW: Store WPI ratio as structured numeric data
    # This prevents fragile parsing from audit_note strings.
    wpi_ratio: Decimal = Decimal("1.00")

    # Human-readable explanation only (not for parsing)
    audit_note: str = ""

    @field_validator("matched_qty")
    @classmethod
    def quantity_must_be_positive(cls, v: Decimal) -> Decimal:
        """
        Ensures quantity is strictly positive.
        Financial records cannot have zero or negative matched quantity.
        """
        if v <= 0:
            raise ValueError("Matched quantity must be positive.")
        return v

    @field_validator("realized_gain_tl")
    @classmethod
    def gain_must_be_decimal(cls, v: Decimal) -> Decimal:
        """
        Ensures realized gain is a Decimal.
        Prevents accidental float contamination.
        """
        if not isinstance(v, Decimal):
            raise TypeError("realized_gain_tl must be Decimal.")
        return v

    @field_validator("wpi_ratio")
    @classmethod
    def wpi_ratio_must_be_positive(cls, v: Decimal) -> Decimal:
        """
        WPI ratio must be positive.
        Values below zero are mathematically invalid.
        """
        if v <= 0:
            raise ValueError("WPI ratio must be positive.")
        return v

    model_config = {
        "frozen": True
    }