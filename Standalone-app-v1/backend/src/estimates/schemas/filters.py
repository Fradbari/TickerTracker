"""
Filter schemas for Estimate queries.

Provides type-safe filtering options for EstimateRepository.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.shared.schemas.validators import validate_date_range


class EstimateFilters(BaseModel):
    """
    Filters for querying Estimate entities.

    All filters are optional and combined with AND logic.

    Attributes:
        ticker_id: Filter by specific ticker
        user_id: Filter by user who created the estimate
        status: Filter by estimate status (OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_NEUTRAL)
        direction: Filter by trade direction (LONG, SHORT)
        created_after: Filter estimates created after this date
        created_before: Filter estimates created before this date
        closed_after: Filter estimates closed after this date
        closed_before: Filter estimates closed before this date
        min_confidence: Minimum AI confidence score (0.0 - 1.0)
        max_confidence: Maximum AI confidence score (0.0 - 1.0)
        include_deleted: Include soft-deleted estimates (default: False)
    """

    ticker_id: UUID | None = Field(default=None, description="Filter by ticker ID")
    user_id: UUID | None = Field(default=None, description="Filter by user ID")
    status: str | None = Field(default=None, description="Filter by status")
    direction: str | None = Field(default=None, description="Filter by direction (LONG/SHORT)")

    created_after: datetime | None = Field(default=None, description="Created after date")
    created_before: datetime | None = Field(default=None, description="Created before date")
    closed_after: datetime | None = Field(default=None, description="Closed after date")
    closed_before: datetime | None = Field(default=None, description="Closed before date")

    min_confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="Min AI confidence")
    max_confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="Max AI confidence")

    include_deleted: bool = Field(default=False, description="Include soft-deleted records")

    @model_validator(mode="after")
    def validate_date_ranges(self) -> "EstimateFilters":
        """Validate that date ranges are logically ordered and within 10 years."""
        if self.created_after is not None and self.created_before is not None:
            validate_date_range(self.created_after, self.created_before)
        if self.closed_after is not None and self.closed_before is not None:
            validate_date_range(self.closed_after, self.closed_before)
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "ticker_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "OPEN",
                "direction": "LONG",
                "created_after": "2026-01-01T00:00:00Z",
                "min_confidence": 0.7,
                "include_deleted": False
            }
        }

    def has_filters(self) -> bool:
        """Check if any filters are applied (excluding include_deleted)."""
        return any([
            self.ticker_id is not None,
            self.user_id is not None,
            self.status is not None,
            self.direction is not None,
            self.created_after is not None,
            self.created_before is not None,
            self.closed_after is not None,
            self.closed_before is not None,
            self.min_confidence is not None,
            self.max_confidence is not None,
        ])
