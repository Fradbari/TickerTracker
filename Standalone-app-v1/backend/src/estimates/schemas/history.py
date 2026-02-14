"""
History schemas - Pydantic models for estimate history and event sourcing.

This module defines response schemas for:
- EstimateSnapshot: State reconstruction at a specific point in time
- AuditEntry: Human-readable audit trail entries
- Change: Detailed change information between timestamps
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.estimates.domain.events import EstimateEventType


class EstimateSnapshot(BaseModel):
    """
    Represents the reconstructed state of an estimate at a specific point in time.
    
    This model is built by replaying events up to a timestamp, providing
    a complete view of what the estimate looked like at that moment.
    
    Attributes:
        estimate_id: Unique identifier of the estimate
        at_timestamp: The point in time this snapshot represents
        ticker_id: Reference to the ticker
        direction: Trade direction (LONG or SHORT)
        status: Current status at the snapshot time
        start_price: Entry price
        target_price: Target profit price
        stop_loss_price: Stop loss price
        target_profit_percent: Target profit percentage
        stop_loss_percent: Stop loss percentage
        exit_price: Exit price if closed (nullable)
        realized_pnl: Realized profit/loss if closed (nullable)
        ai_model: AI model used (nullable)
        ai_confidence: AI confidence score (nullable)
        ai_reasoning: AI reasoning text (nullable)
        created_at: When the estimate was originally created
        closed_at: When closed (nullable)
        event_count: Number of events that occurred up to this snapshot
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estimate_id": "123e4567-e89b-12d3-a456-426614174000",
                "at_timestamp": "2024-01-15T14:30:00Z",
                "ticker_id": "987fbc97-4bed-5078-9f07-9141ba07c9f3",
                "direction": "LONG",
                "status": "OPEN",
                "start_price": "100.00",
                "target_price": "115.00",
                "stop_loss_price": "95.00",
                "target_profit_percent": "15.00",
                "stop_loss_percent": "5.00",
                "exit_price": None,
                "realized_pnl": None,
                "ai_model": "gpt-4",
                "ai_confidence": "75.00",
                "ai_reasoning": "Strong technical indicators",
                "created_at": "2024-01-15T10:00:00Z",
                "closed_at": None,
                "event_count": 3
            }
        }
    )
    
    # Identity
    estimate_id: UUID = Field(..., description="Unique identifier of the estimate")
    at_timestamp: datetime = Field(..., description="Point in time this snapshot represents")
    
    # Relationships
    ticker_id: UUID = Field(..., description="Reference to ticker")
    user_id: Optional[UUID] = Field(None, description="User who created the estimate")
    
    # Trade parameters
    direction: str = Field(..., description="Trade direction (LONG or SHORT)")
    status: str = Field(..., description="Status at this point in time")
    
    # Prices (using Decimal for financial precision)
    start_price: Decimal = Field(..., description="Entry price", decimal_places=4)
    target_price: Decimal = Field(..., description="Target profit price", decimal_places=4)
    stop_loss_price: Decimal = Field(..., description="Stop loss price", decimal_places=4)
    
    # Percentages
    target_profit_percent: Decimal = Field(..., description="Target profit %", decimal_places=4)
    stop_loss_percent: Decimal = Field(..., description="Stop loss %", decimal_places=4)
    
    # Exit information
    exit_price: Optional[Decimal] = Field(None, description="Exit price if closed", decimal_places=4)
    realized_pnl: Optional[Decimal] = Field(None, description="Realized PnL if closed", decimal_places=4)
    
    # AI metadata
    ai_model: Optional[str] = Field(None, description="AI model used for estimate")
    ai_confidence: Optional[Decimal] = Field(None, description="AI confidence score", decimal_places=2)
    ai_reasoning: Optional[str] = Field(None, description="AI reasoning/explanation")
    
    # Timestamps
    created_at: datetime = Field(..., description="When estimate was created")
    closed_at: Optional[datetime] = Field(None, description="When estimate was closed")
    
    # Metadata
    event_count: int = Field(..., description="Number of events up to this snapshot", ge=0)


class AuditEntry(BaseModel):
    """
    Human-readable audit trail entry for an estimate event.
    
    This model provides a user-friendly representation of an event,
    including formatted descriptions of what changed and why.
    
    Attributes:
        event_id: Unique identifier of the event
        estimate_id: Reference to the estimate
        event_type: Type of event that occurred
        timestamp: When the event occurred
        description: Human-readable description of what happened
        changed_fields: List of field names that were modified (if applicable)
        old_values: Previous values of changed fields (if applicable)
        new_values: New values of changed fields (if applicable)
        user_id: User who triggered the event (nullable for system events)
        is_system_event: True if event was triggered automatically
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "456e7890-e12c-34d5-b678-526614174123",
                "estimate_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "PRICE_UPDATED",
                "timestamp": "2024-01-15T12:00:00Z",
                "description": "Target price updated from $110.00 to $115.00 (+4.5%)",
                "changed_fields": ["target_price", "target_profit_percent"],
                "old_values": {"target_price": "110.00", "target_profit_percent": "10.00"},
                "new_values": {"target_price": "115.00", "target_profit_percent": "15.00"},
                "user_id": "789fbc97-5bed-6078-af07-a141ba07c9f4",
                "is_system_event": False
            }
        }
    )
    
    # Identity
    event_id: UUID = Field(..., description="Unique identifier of the event")
    estimate_id: UUID = Field(..., description="Reference to the estimate")
    event_type: EstimateEventType = Field(..., description="Type of event")
    timestamp: datetime = Field(..., description="When the event occurred")
    
    # Human-readable information
    description: str = Field(..., description="Human-readable description of what happened")
    
    # Change details
    changed_fields: Optional[list[str]] = Field(None, description="Fields that were modified")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    
    # Actor information
    user_id: Optional[UUID] = Field(None, description="User who triggered event")
    is_system_event: bool = Field(..., description="True if triggered automatically")


class Change(BaseModel):
    """
    Detailed change information for a specific field or set of fields.
    
    Represents a logical change between two points in time, potentially
    aggregating multiple events that affected the same fields.
    
    Attributes:
        field_name: Name of the field that changed
        old_value: Previous value (at start timestamp)
        new_value: New value (at end timestamp)
        changed_at: When the change occurred
        event_id: ID of the event that caused this change
        event_type: Type of event that caused this change
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_name": "status",
                "old_value": "OPEN",
                "new_value": "CLOSED_WIN",
                "changed_at": "2024-01-20T15:30:00Z",
                "event_id": "789abc12-f34e-56d7-c890-d26614174456",
                "event_type": "CLOSED"
            }
        }
    )
    
    field_name: str = Field(..., description="Name of the field that changed")
    old_value: Any = Field(..., description="Previous value")
    new_value: Any = Field(..., description="New value")
    changed_at: datetime = Field(..., description="When the change occurred")
    event_id: UUID = Field(..., description="ID of the event that caused this change")
    event_type: EstimateEventType = Field(..., description="Type of event")


class EstimateHistorySummary(BaseModel):
    """
    Summary of an estimate's complete history.
    
    Provides high-level statistics about the estimate's lifetime and events.
    
    Attributes:
        estimate_id: Unique identifier of the estimate
        total_events: Total number of events
        first_event_at: Timestamp of first event (creation)
        last_event_at: Timestamp of most recent event
        event_type_counts: Count of events by type
        total_changes: Number of distinct field changes
        is_closed: Whether the estimate is currently closed
    """
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estimate_id": "123e4567-e89b-12d3-a456-426614174000",
                "total_events": 7,
                "first_event_at": "2024-01-15T10:00:00Z",
                "last_event_at": "2024-01-20T15:30:00Z",
                "event_type_counts": {
                    "CREATED": 1,
                    "PRICE_UPDATED": 3,
                    "UPDATED": 2,
                    "CLOSED": 1
                },
                "total_changes": 12,
                "is_closed": True
            }
        }
    )
    
    estimate_id: UUID = Field(..., description="Unique identifier of the estimate")
    total_events: int = Field(..., description="Total number of events", ge=0)
    first_event_at: datetime = Field(..., description="Timestamp of first event")
    last_event_at: datetime = Field(..., description="Timestamp of most recent event")
    event_type_counts: Dict[str, int] = Field(..., description="Count of events by type")
    total_changes: int = Field(..., description="Number of distinct field changes", ge=0)
    is_closed: bool = Field(..., description="Whether estimate is currently closed")
