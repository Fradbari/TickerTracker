"""
Estimates domain events - EstimateEvent model for Event Sourcing.

This module defines the SQLAlchemy model for event sourcing of estimates.
Events are immutable records that track all changes to estimates over time.
"""

import uuid
import enum
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, 
    Index, Enum as SQLEnum, CheckConstraint, Integer, select
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infra.database import Base


class EstimateEventType(str, enum.Enum):
    """
    Types of events that can occur on an estimate.
    
    Events provide a complete audit trail and enable event sourcing patterns.
    """
    CREATED = "CREATED"           # Estimate was created
    UPDATED = "UPDATED"           # Estimate metadata was updated
    PRICE_UPDATED = "PRICE_UPDATED"  # Start/target/stop prices were updated
    TARGET_HIT = "TARGET_HIT"     # Target price was reached
    STOP_HIT = "STOP_HIT"         # Stop loss was hit
    CLOSED = "CLOSED"             # Estimate was closed (manually or automatically)
    REOPENED = "REOPENED"         # Closed estimate was reopened


class EstimateEvent(Base):
    """
    Event sourcing entity for estimate changes.
    
    This table is append-only and immutable. Events are never updated or deleted,
    providing a complete audit trail of all estimate changes.
    
    Attributes:
        id: Unique identifier (UUID)
        estimate_id: Reference to the estimate
        event_type: Type of event that occurred
        event_data: JSON data specific to this event type
        user_id: User who triggered the event (nullable for system events)
        timestamp: When the event occurred (with timezone)
    
    Event Data Examples:
        CREATED: {"initial_price": 100.00, "direction": "LONG"}
        UPDATED: {"changed_fields": ["ai_confidence"], "old_values": {...}}
        PRICE_UPDATED: {"old_target": 110.00, "new_target": 115.00}
        TARGET_HIT: {"exit_price": 110.50, "profit": 10.50}
        STOP_HIT: {"exit_price": 95.00, "loss": -5.00}
        CLOSED: {"reason": "manual", "final_pnl": 5.50}
        REOPENED: {"reason": "error_correction"}
    """
    
    __tablename__ = "estimate_events"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    
    # Foreign key to Estimate
    estimate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("estimates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the estimate this event belongs to"
    )
    
    # Event metadata
    event_type = Column(
        SQLEnum(EstimateEventType, name="estimate_event_type"),
        nullable=False,
        doc="Type of event that occurred"
    )
    
    # Event payload as JSON for flexibility (will be JSONB on PostgreSQL)
    event_data = Column(
        JSON,
        nullable=False,
        default=dict,
        doc="JSON data specific to this event type"
    )
    
    # User tracking
    user_id = Column(
        UUID(as_uuid=True),
        # ForeignKey to User table will be added later
        nullable=True,
        doc="User who triggered the event (null for system events)"
    )
    
    # Timestamp with timezone (required for event sourcing)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="When the event occurred (UTC)"
    )
    
    # Outbox pattern fields for reliable event processing
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="When event was successfully processed to Drive"
    )
    
    retry_count = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of processing retry attempts"
    )
    
    error = Column(
        String(500),
        nullable=True,
        doc="Last error message if processing failed"
    )
    
    # Relationship to Estimate
    estimate = relationship(
        "Estimate",
        backref="events",
        lazy="select"
    )
    
    # Indexes and constraints
    __table_args__ = (
        # Composite index for efficient timeline queries
        Index(
            "ix_estimate_event_timeline",
            "estimate_id",
            "timestamp",
            postgresql_ops={"timestamp": "DESC"}
        ),
        
        # Index on event_type for filtering by event type
        Index("ix_estimate_event_type", "event_type"),
        
        # Ensure timestamp has timezone info
        CheckConstraint(
            "timestamp IS NOT NULL",
            name="ck_estimate_event_timestamp_not_null"
        ),
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<EstimateEvent(id={self.id}, estimate_id={self.estimate_id}, "
            f"type={self.event_type.value}, timestamp={self.timestamp})>"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "id": str(self.id),
            "estimate_id": str(self.estimate_id),
            "event_type": self.event_type.value,
            "event_data": self.event_data,
            "user_id": str(self.user_id) if self.user_id else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "retry_count": self.retry_count,
            "error": self.error,
        }
    
    # Outbox pattern methods
    
    def mark_processed(self) -> None:
        """Mark event as successfully processed."""
        self.processed_at = datetime.now(timezone.utc)
        self.error = None
    
    def mark_failed(self, error_msg: str) -> None:
        """Mark event processing failed, increment retry."""
        self.retry_count += 1
        self.error = error_msg[:500]  # Truncate to DB limit
    
    def can_retry(self) -> bool:
        """Check if event can be retried (max 5 attempts)."""
        return self.retry_count < 5 and self.processed_at is None
    
    def is_dead_letter(self) -> bool:
        """Check if event is dead letter (max retries exceeded)."""
        return self.retry_count >= 5 and self.processed_at is None
    
    @classmethod
    async def get_unprocessed(cls, session: AsyncSession, limit: int = 100) -> List['EstimateEvent']:
        """Get unprocessed events for outbox processing."""
        result = await session.execute(
            select(cls)
            .where(cls.processed_at.is_(None))
            .where(cls.retry_count < 5)
            .order_by(cls.timestamp.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def get_dead_letters(cls, session: AsyncSession) -> List['EstimateEvent']:
        """Get dead letter events (max retries exceeded)."""
        result = await session.execute(
            select(cls)
            .where(cls.processed_at.is_(None))
            .where(cls.retry_count >= 5)
            .order_by(cls.timestamp.asc())
        )
        return list(result.scalars().all())
