"""
Command schemas for Estimate operations.

These Pydantic models define the input contracts for estimate service methods.
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.shared.schemas.validators import sanitize_text, validate_price


class CreateEstimateCommand(BaseModel):
    """
    Command to create a new estimate.

    Attributes:
        ticker_id: UUID of the ticker to estimate
        direction: Trading direction ('LONG' or 'SHORT')
        target_profit_percent: Target profit percentage (e.g., 10.0 for 10%)
        stop_loss_percent: Stop loss percentage (e.g., 5.0 for 5%)
        user_id: Optional UUID of the user creating the estimate
        ai_model: Optional AI model identifier
        ai_confidence: Optional AI confidence score (0-100)
        ai_reasoning: Optional AI reasoning text

    Note:
        - start_price, target_price, and stop_loss_price are calculated automatically
          from current market price and percentages
        - Percentages must be positive numbers
    """

    ticker_id: UUID = Field(..., description="Ticker ID to create estimate for")
    direction: str = Field(..., description="Trade direction: LONG or SHORT")

    target_profit_percent: Decimal = Field(
        ...,
        gt=0,
        le=1000,
        description="Target profit percentage (e.g., 10.0 for 10%)"
    )

    stop_loss_percent: Decimal = Field(
        ...,
        gt=0,
        le=100,
        description="Stop loss percentage (e.g., 5.0 for 5%)"
    )

    user_id: UUID | None = Field(default=None, description="User creating the estimate")
    ai_model: str | None = Field(default=None, max_length=100, description="AI model used")
    ai_confidence: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="AI confidence score (0-100)"
    )
    ai_reasoning: str | None = Field(default=None, description="AI reasoning text")

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, v: str) -> str:
        """Validate direction is either LONG or SHORT."""
        if v.upper() not in ("LONG", "SHORT"):
            raise ValueError("Direction must be 'LONG' or 'SHORT'")
        return v.upper()

    @field_validator("ai_reasoning")
    @classmethod
    def validate_ai_reasoning(cls, v: str | None) -> str | None:
        """Strip HTML and trim ai_reasoning to 2000 characters."""
        if v is None:
            return v
        return sanitize_text(v, max_len=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "ticker_id": "7884ff09-bb49-403c-8bc2-3d9bbfdb810b",
                "direction": "LONG",
                "target_profit_percent": 15.0,
                "stop_loss_percent": 5.0,
                "ai_model": "gpt-4",
                "ai_confidence": 75.0,
                "ai_reasoning": "Strong technical indicators suggest upward momentum"
            }
        }


class UpdateEstimateCommand(BaseModel):
    """
    Command to update an existing estimate.

    Attributes:
        estimate_id: UUID of the estimate to update
        target_profit_percent: Optional new target profit percentage
        stop_loss_percent: Optional new stop loss percentage
        ai_confidence: Optional updated AI confidence score
        ai_reasoning: Optional updated AI reasoning
        user_id: Optional UUID of user performing the update

    Note:
        - All fields are optional (only provided fields will be updated)
        - Updating percentages will recalculate target_price and stop_loss_price
        - Cannot update estimate if status is not OPEN
    """

    estimate_id: UUID = Field(..., description="Estimate ID to update")

    target_profit_percent: Decimal | None = Field(
        default=None,
        gt=0,
        le=1000,
        description="New target profit percentage"
    )

    stop_loss_percent: Decimal | None = Field(
        default=None,
        gt=0,
        le=100,
        description="New stop loss percentage"
    )

    ai_confidence: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Updated AI confidence score"
    )

    ai_reasoning: str | None = Field(
        default=None,
        description="Updated AI reasoning"
    )

    user_id: UUID | None = Field(
        default=None,
        description="User performing the update"
    )

    @field_validator("target_profit_percent", "stop_loss_percent", "ai_confidence")
    @classmethod
    def validate_positive(cls, v: Decimal | None) -> Decimal | None:
        """Ensure percentages are positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Percentages must be positive")
        return v

    @field_validator("ai_reasoning")
    @classmethod
    def validate_ai_reasoning(cls, v: str | None) -> str | None:
        """Strip HTML and trim ai_reasoning to 2000 characters."""
        if v is None:
            return v
        return sanitize_text(v, max_len=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "estimate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "target_profit_percent": 20.0,
                "ai_confidence": 80.0,
                "ai_reasoning": "Updated analysis shows stronger momentum"
            }
        }


class CloseEstimateCommand(BaseModel):
    """
    Command to manually close an estimate.

    Attributes:
        estimate_id: UUID of the estimate to close
        exit_price: Actual exit price
        reason: Reason for closing (e.g., 'manual', 'target_hit', 'stop_hit')
        user_id: Optional UUID of user closing the estimate

    Note:
        - PnL will be calculated automatically based on entry and exit prices
        - Status will be set to CLOSED_WIN, CLOSED_LOSS, or CLOSED_MANUAL
        - Cannot close an estimate that is already closed
    """

    estimate_id: UUID = Field(..., description="Estimate ID to close")
    exit_price: Decimal = Field(..., gt=0, description="Actual exit price")
    reason: str = Field(..., description="Reason for closing")
    user_id: UUID | None = Field(default=None, description="User closing the estimate")

    @field_validator("exit_price")
    @classmethod
    def validate_exit_price(cls, v: Decimal) -> Decimal:
        """Validate exit_price is a positive, in-range price value."""
        return validate_price(v)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate reason is not empty."""
        if not v or not v.strip():
            raise ValueError("Reason cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "estimate_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "exit_price": 115.50,
                "reason": "Target reached manually",
                "user_id": "user-123-uuid"
            }
        }

