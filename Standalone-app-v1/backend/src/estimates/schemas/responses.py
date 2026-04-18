"""
Response schemas for Estimate API endpoints.

This module defines Pydantic models for API responses, converting
SQLAlchemy Estimate entities to JSON-serializable structures.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TickerNestedResponse(BaseModel):
    symbol: str

    model_config = ConfigDict(from_attributes=True)


class EstimateResponse(BaseModel):
    """
    Standard response schema for a single estimate.

    Used for:
    - GET /api/estimates/{id}
    - POST /api/estimates (created estimate)
    - PATCH /api/estimates/{id} (updated estimate)

    Attributes:
        id: Unique identifier
        ticker_id: Reference to ticker
        user_id: Reference to user (nullable)
 (LONG        status: Current status
        start_price: Entry price
        target_price: Target profit price
        stop_loss_price: Stop loss price
        target_profit_percent: Target profit percentage
        stop_loss_percent: Stop loss percentage
        exit_price: Exit price (nullable until closed)
        realized_pnl: Realized PnL (nullable until closed)
        ai_model: AI model used (nullable)
        ai_confidence: AI confidence score (nullable)
        ai_reasoning: AI reasoning (nullable)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        closed_at: Close timestamp (nullable)
        is_deleted: Soft delete flag
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "ticker_id": "987fbc97-4bed-5078-9f07-9141ba07c9f3",
                "user_id": "456e7890-e12c-34d5-b678-526614174001",
                "status": "OPEN",
                "start_price": "100.00",
                "target_price": "115.00",
                "stop_loss_price": "95.00",
                "target_profit_percent": "15.0",
                "stop_loss_percent": "5.0",
                "exit_price": None,
                "realized_pnl": None,
                "ai_model": "gpt-4",
                "ai_confidence": "75.0",
                "ai_reasoning": "Strong bullish indicators",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z",
                "closed_at": None,
                "is_deleted": False,
            }
        }
    )

    id: UUID
    ticker_id: UUID
    user_id: UUID | None = None
    status: str
    start_price: Decimal
    target_price: Decimal
    stop_loss_price: Decimal
    target_profit_percent: Decimal
    stop_loss_percent: Decimal
    exit_price: Decimal | None = None
    realized_pnl: Decimal | None = None
    realized_pnl_percent: Decimal | None = None
    ai_model: str | None = None
    ai_version: str | None = None
    ai_confidence: Decimal | None = None
    ai_reasoning: str | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    is_deleted: bool
    ticker: TickerNestedResponse | None = None


class EstimateListResponse(BaseModel):
    """
    Response schema for paginated list of estimates.

    Used for: GET /api/estimates

    Attributes:
        items: List of estimates
        total: Total count of estimates matching filters
        page_info: Pagination information
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "ticker_id": "987fbc97-4bed-5078-9f07-9141ba07c9f3",
                        "status": "OPEN",
                        "start_price": "100.00",
                        "target_price": "115.00",
                        "stop_loss_price": "95.00",
                        "created_at": "2024-01-15T10:00:00Z",
                    }
                ],
                "total": 42,
                "page_info": {
                    "has_next_page": True,
                    "has_previous_page": False,
                    "next_cursor": "eyJpZCI6IjEyMyJ9",
                    "previous_cursor": None,
                },
            }
        }
    )

    items: list[EstimateResponse]
    total: int = Field(..., description="Total number of items matching filters")
    page_info: dict = Field(..., description="Pagination information")


class EstimateCreatedResponse(BaseModel):
    """
    Response schema for successful estimate creation.

    Includes the created estimate and a message.

    Used for: POST /api/estimates
    """

    estimate: EstimateResponse
    message: str = Field(default="Estimate created successfully")


class EstimateUpdatedResponse(BaseModel):
    """
    Response schema for successful estimate update.

    Includes the updated estimate and a message.

    Used for: PATCH /api/estimates/{id}
    """

    estimate: EstimateResponse
    message: str = Field(default="Estimate updated successfully")


class EstimateDeletedResponse(BaseModel):
    """
    Response schema for successful estimate deletion/closure.

    Used for: DELETE /api/estimates/{id}
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "CLOSED_MANUAL",
                "message": "Estimate closed successfully",
            }
        }
    )

    id: UUID
    status: str
    message: str = Field(default="Estimate deleted successfully")


class EstimateHistoryResponse(BaseModel):
    """
    Response schema for estimate history/audit trail.

    Used for: GET /api/estimates/{id}/history

    Attributes:
        estimate_id: UUID of the estimate
        audit_trail: List of audit entries
        summary: History summary statistics
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estimate_id": "123e4567-e89b-12d3-a456-426614174000",
                "audit_trail": [
                    {
                        "event_id": "789abc12-f34e-56d7-c890-d26614174456",
                        "event_type": "CREATED",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "description": "Estimate created: LONG at $100.00",
                    }
                ],
                "summary": {
                    "total_events": 5,
                    "first_event_at": "2024-01-15T10:00:00Z",
                    "last_event_at": "2024-01-20T15:30:00Z",
                },
            }
        }
    )

    estimate_id: UUID
    audit_trail: list
    summary: dict
