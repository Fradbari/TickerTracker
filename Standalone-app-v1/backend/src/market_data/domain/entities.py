"""
Market data domain entities - Ticker model.

This module defines the SQLAlchemy model for ticker/symbol information.
"""

import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, Index, String, ForeignKey, DECIMAL, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.shared.infra.database import Base


class Ticker(Base):
    """
    Ticker entity representing a tradable financial instrument.

    Attributes:
        id: Unique identifier (UUID)
        symbol: Trading symbol (e.g., 'AAPL', 'MSFT')
        name: Full company/asset name
        exchange: Exchange where traded (e.g., 'NASDAQ', 'NYSE')
        currency: Trading currency (ISO 4217 code)
        asset_type: Type of asset (stock, etf, crypto)
        created_at: Timestamp of record creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "tickers"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Core fields
    symbol = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        doc="Trading symbol (unique identifier)"
    )

    name = Column(
        String(255),
        nullable=False,
        doc="Full name of the instrument"
    )

    exchange = Column(
        String(50),
        nullable=True,
        doc="Exchange where instrument is traded"
    )

    currency = Column(
        String(3),
        nullable=False,
        default="USD",
        doc="Currency code (ISO 4217)"
    )

    asset_type = Column(
        String(20),
        nullable=False,
        doc="Type of asset: stock, etf, or crypto"
    )

    # Audit timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        doc="Timestamp of record creation"
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        doc="Timestamp of last update"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "asset_type IN ('stock', 'etf', 'crypto')",
            name="ck_ticker_asset_type"
        ),
        Index("ix_ticker_symbol", "symbol"),
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Ticker(symbol={self.symbol!r}, name={self.name!r}, type={self.asset_type!r})>"


class Candle(Base):
    """
    Historical open-high-low-close (OHLCV) candle for a ticker.
    """
    __tablename__ = "candles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    ticker_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tickers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp_start = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(DECIMAL(14, 4), nullable=False)
    high_price = Column(DECIMAL(14, 4), nullable=False)
    low_price = Column(DECIMAL(14, 4), nullable=False)
    close_price = Column(DECIMAL(14, 4), nullable=False)
    volume = Column(BigInteger, nullable=True)

    __table_args__ = (
        UniqueConstraint('ticker_id', 'timestamp_start', name='uq_candle_ticker_timestamp'),
        Index('ix_candles_ticker_time', 'ticker_id', 'timestamp_start', postgresql_using='btree'),
    )

    ticker = relationship("Ticker", backref="candles")

    def __repr__(self) -> str:
        return f"<Candle(ticker_id={self.ticker_id!r}, time={self.timestamp_start!r}, close={self.close_price})>"
