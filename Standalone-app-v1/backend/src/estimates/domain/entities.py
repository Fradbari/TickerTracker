"""
Estimates domain entities - Estimate model.

This module defines the SQLAlchemy model for trading estimates/predictions.
"""

import enum
import uuid

from sqlalchemy import (
    DECIMAL,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.shared.infra.database import Base


class EstimateStatus(str, enum.Enum):
    """Status of an estimate/prediction."""
    OPEN = "OPEN"
    CLOSED_WIN = "CLOSED_WIN"
    CLOSED_LOSS = "CLOSED_LOSS"
    CLOSED_MANUAL = "CLOSED_MANUAL"
    EXPIRED = "EXPIRED"


class Estimate(Base):
    """
    Estimate entity representing a trading prediction/estimate.

    Attributes:
        id: Unique identifier (UUID)
        ticker_id: Reference to the traded ticker
        user_id: Reference to the user (nullable for now)
        start_price: Entry price for the estimate
        target_price: Target price for profit
        stop_loss_price: Stop loss price
        target_profit_percent: Target profit percentage
        stop_loss_percent: Stop loss percentage
        status: Current status of the estimate
        ai_model: AI model used for the estimate
        ai_confidence: AI confidence score (0-100)
        ai_reasoning: AI reasoning/explanation
        created_at: Timestamp of estimate creation
        updated_at: Timestamp of last update
        closed_at: Timestamp when estimate was closed (nullable)
        is_deleted: Soft delete flag
        deleted_at: Timestamp when estimate was soft deleted (nullable)
        exit_price: Actual exit price (nullable until closed)
        realized_pnl: Realized profit/loss (nullable until closed)
    """

    __tablename__ = "estimates"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Foreign keys
    ticker_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tickers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        doc="Reference to the ticker being predicted"
    )

    user_id = Column(
        UUID(as_uuid=True),
        # ForeignKey to User table will be added later
        nullable=True,
        doc="Reference to the user who created the estimate"
    )

    # Price fields (using DECIMAL for precision)
    start_price = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Entry price for the estimate"
    )

    target_price = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Target price for profit"
    )

    stop_loss_price = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Stop loss price"
    )

    # Target percentages
    target_profit_percent = Column(
        DECIMAL(8, 4),
        nullable=False,
        doc="Target profit percentage"
    )

    stop_loss_percent = Column(
        DECIMAL(8, 4),
        nullable=False,
        doc="Stop loss percentage"
    )

    # Status
    status = Column(
        SQLEnum(EstimateStatus, name="estimate_status"),
        nullable=False,
        default=EstimateStatus.OPEN,
        index=True,
        doc="Current status of the estimate"
    )

    # AI-related fields
    ai_model = Column(
        String(100),
        nullable=True,
        doc="AI model identifier used for the estimate"
    )

    ai_version = Column(
        String(50),
        nullable=True,
        doc="AI model version used for the estimate"
    )

    ai_confidence = Column(
        DECIMAL(5, 2),
        nullable=True,
        doc="AI confidence score (0-100)"
    )

    ai_reasoning = Column(
        Text,
        nullable=True,
        doc="AI reasoning and explanation for the estimate"
    )

    # Date fields
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        doc="Timestamp of estimate creation"
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp of last update"
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when estimate was closed"
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
        index=True,
        doc="Soft delete flag"
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when estimate was soft deleted"
    )

    # Exit fields (nullable until closed)
    exit_price = Column(
        DECIMAL(10, 4),
        nullable=True,
        doc="Actual exit price (set when closed)"
    )

    realized_pnl = Column(
        DECIMAL(12, 4),
        nullable=True,
        doc="Realized profit/loss (set when closed)"
    )

    realized_pnl_percent = Column(
        DECIMAL(10, 4),
        nullable=True,
        doc="Realized profit/loss percentage (set when closed)"
    )

    # Relationship to Ticker
    ticker = relationship(
        "Ticker",
        backref="estimates",
        lazy="select"
    )

    # Indexes and constraints
    __table_args__ = (
        # Standard indexes
        Index("ix_estimate_ticker_id", "ticker_id"),
        Index("ix_estimate_status", "status"),
        Index("ix_estimate_created_at", "created_at"),
        Index("ix_estimate_is_deleted", "is_deleted"),

        # Partial index for open estimates (most frequent query)
        Index(
            "ix_estimate_open_status",
            "status",
            postgresql_where=text("status = 'OPEN'")
        ),

        # Check constraints
        CheckConstraint(
            "ai_confidence IS NULL OR (ai_confidence >= 0 AND ai_confidence <= 100)",
            name="ck_estimate_ai_confidence_range"
        ),
        CheckConstraint(
            "start_price > 0",
            name="ck_estimate_start_price_positive"
        ),
        CheckConstraint(
            "target_price > 0",
            name="ck_estimate_target_price_positive"
        ),
        CheckConstraint(
            "stop_loss_price > 0",
            name="ck_estimate_stop_loss_price_positive"
        ),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Estimate(id={self.id}, ticker_id={self.ticker_id}, "
            f"status={self.status.value}, )>"
        )

