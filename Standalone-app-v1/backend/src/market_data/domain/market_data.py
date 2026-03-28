"""
Market data domain entities - MarketData model for OHLCV historical data.

This module defines the SQLAlchemy model for historical market data (OHLCV).
Data lineage tracking (data_source, source_timestamp, ingestion_timestamp,
quality_score) is provided by the ``LineageTracked`` mixin (TASK 3.9).
"""

from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.shared.domain.lineage import LineageTracked
from src.shared.infra.database import Base


class MarketData(LineageTracked, Base):
    """
    Market data entity representing OHLCV (Open-High-Low-Close-Volume) historical data.

    This table stores daily market data for tickers with data lineage tracking.
    Uses composite primary key (ticker_id, date) to ensure no duplicates per ticker/day.

    Lineage columns (from ``LineageTracked`` mixin — TASK 3.9):
        data_source:         DataSource enum value stored as VARCHAR(50)
        source_timestamp:    When data was generated at the source (nullable)
        ingestion_timestamp: When data entered our system (server-side auto-set)
        quality_score:       0.00–1.00; computed from freshness and completeness

    Attributes:
        ticker_id:           Reference to the ticker (part of composite PK)
        date:                Trading date (part of composite PK)
        open:                Opening price for the day
        high:                Highest price during the day
        low:                 Lowest price during the day
        close:               Closing price for the day
        volume:              Trading volume (number of shares/units traded)

    Data Quality Score Guidelines:
        1.00 = Official exchange data
        0.80-0.99 = Reliable third-party provider (e.g., Yahoo Finance)
        0.50-0.79 = Aggregated/derived data
        0.00-0.49 = Estimated/low-confidence data
    """

    __tablename__ = "market_data"

    # Composite Primary Key: ticker_id + date
    ticker_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tickers.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        doc="Reference to the ticker"
    )

    date = Column(
        Date,
        primary_key=True,
        nullable=False,
        doc="Trading date (part of composite PK)"
    )

    # OHLCV fields (all prices use DECIMAL for precision)
    open = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Opening price for the day"
    )

    high = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Highest price during the day"
    )

    low = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Lowest price during the day"
    )

    close = Column(
        DECIMAL(10, 4),
        nullable=False,
        doc="Closing price for the day"
    )

    volume = Column(
        BigInteger,
        nullable=False,
        doc="Trading volume (number of shares/units traded)"
    )

    # NOTE: data_source, source_timestamp, ingestion_timestamp, quality_score
    # are inherited from the LineageTracked mixin (TASK 3.9).

    # Relationship to Ticker
    ticker = relationship(
        "Ticker",
        backref="market_data",
        lazy="select"
    )

    # Indexes and constraints
    __table_args__ = (
        # Unique constraint on composite PK (implicit from primary_key=True)
        # but explicitly defined for clarity
        Index(
            "ix_market_data_ticker_date",
            "ticker_id",
            "date",
            unique=True
        ),

        # Index on date for time-series queries
        Index("ix_market_data_date", "date"),

        # Check constraints for data validation
        CheckConstraint(
            "open > 0",
            name="ck_market_data_open_positive"
        ),
        CheckConstraint(
            "high > 0",
            name="ck_market_data_high_positive"
        ),
        CheckConstraint(
            "low > 0",
            name="ck_market_data_low_positive"
        ),
        CheckConstraint(
            "close > 0",
            name="ck_market_data_close_positive"
        ),
        CheckConstraint(
            "volume >= 0",
            name="ck_market_data_volume_non_negative"
        ),
        CheckConstraint(
            "high >= low",
            name="ck_market_data_high_gte_low"
        ),
        CheckConstraint(
            "high >= open",
            name="ck_market_data_high_gte_open"
        ),
        CheckConstraint(
            "high >= close",
            name="ck_market_data_high_gte_close"
        ),
        CheckConstraint(
            "low <= open",
            name="ck_market_data_low_lte_open"
        ),
        CheckConstraint(
            "low <= close",
            name="ck_market_data_low_lte_close"
        ),
        CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0.00 AND quality_score <= 1.00)",
            name="ck_market_data_quality_score_range"
        ),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<MarketData(ticker_id={self.ticker_id}, date={self.date}, "
            f"close={self.close}, volume={self.volume})>"
        )

    @property
    def day_range(self) -> Decimal:
        """Calculate the day's price range (high - low)."""
        return self.high - self.low

    @property
    def day_change(self) -> Decimal:
        """Calculate the day's price change (close - open)."""
        return self.close - self.open

    @property
    def day_change_percent(self) -> Decimal:
        """Calculate the day's price change percentage."""
        if self.open == 0:
            return Decimal("0")
        return ((self.close - self.open) / self.open) * Decimal("100")
