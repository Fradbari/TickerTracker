"""Repository for MarketData data access."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, bindparam, func, insert, select, text, update
from sqlalchemy.types import Date
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.market_data.domain.market_data import MarketData


class MarketDataRow:
    """Data class for market data row to upsert."""

    def __init__(
        self,
        ticker_id: UUID,
        date: date,
        open: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: int,
        data_source: str = "yahoo",
        quality_score: Optional[Decimal] = None,
    ):
        self.ticker_id = ticker_id
        self.date = date
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.data_source = data_source
        self.quality_score = quality_score or Decimal("0.80")


class AggregatedData:
    """Data class for aggregated market data."""

    def __init__(
        self,
        period_start: date,
        period_end: date,
        open: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: int,
        interval: str,
    ):
        self.period_start = period_start
        self.period_end = period_end
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.interval = interval


class MarketDataRepository:
    """Repository for CRUD operations on MarketData entities."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def upsert_daily(
        self, ticker_id: UUID, data_rows: List[MarketDataRow]
    ) -> int:
        """
        Upsert market data rows into the database.

        Inserts new rows or updates existing rows where (ticker_id, date) conflict.
        Uses PostgreSQL ON CONFLICT ... DO UPDATE for atomic operation.

        Args:
            ticker_id: The ticker ID (for reference only, included in rows)
            data_rows: List of MarketDataRow objects to upsert

        Returns:
            Number of rows inserted/updated

        Example:
            >>> rows = [
            ...     MarketDataRow(ticker_id, date(2026, 1, 1), ..., data_source="yahoo"),
            ...     MarketDataRow(ticker_id, date(2026, 1, 2), ..., data_source="yahoo"),
            ... ]
            >>> count = await repo.upsert_daily(ticker_id, rows)
        """
        if not data_rows:
            return 0

        async with self._session_factory() as session:
            async with session.begin():
                values = [
                    {
                        "ticker_id": row.ticker_id,
                        "date": row.date,
                        "open": row.open,
                        "high": row.high,
                        "low": row.low,
                        "close": row.close,
                        "volume": row.volume,
                        "data_source": row.data_source,
                        "quality_score": row.quality_score,
                        "ingested_at": func.now(),
                    }
                    for row in data_rows
                ]

                stmt = pg_insert(MarketData).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["ticker_id", "date"],
                    set_={
                        MarketData.open: stmt.excluded.open,
                        MarketData.high: stmt.excluded.high,
                        MarketData.low: stmt.excluded.low,
                        MarketData.close: stmt.excluded.close,
                        MarketData.volume: stmt.excluded.volume,
                        MarketData.data_source: stmt.excluded.data_source,
                        MarketData.quality_score: stmt.excluded.quality_score,
                        MarketData.ingested_at: func.now(),
                    },
                )

                result = await session.execute(stmt)

            return result.rowcount

    async def get_history(
        self,
        ticker_id: UUID,
        start: date,
        end: date,
    ) -> List[MarketData]:
        """
        Get historical market data for a ticker between dates.

        Args:
            ticker_id: The ticker ID
            start: Start date (inclusive)
            end: End date (inclusive)

        Returns:
            List of MarketData ordered by date ascending
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(MarketData)
                .where(
                    and_(
                        MarketData.ticker_id == ticker_id,
                        MarketData.date >= start,
                        MarketData.date <= end,
                    )
                )
                .order_by(MarketData.date.asc())
            )
            return list(result.scalars().all())

    async def get_latest_price(self, ticker_id: UUID) -> Optional[MarketData]:
        """
        Get the most recent market data for a ticker.

        Args:
            ticker_id: The ticker ID

        Returns:
            Most recent MarketData or None if no data exists
        """
        async with self._session_factory() as session:
            result = await session.execute(
                select(MarketData)
                .where(MarketData.ticker_id == ticker_id)
                .order_by(MarketData.date.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    async def get_latest_prices_batch(
        self, ticker_ids: List[UUID]
    ) -> Dict[UUID, MarketData]:
        """
        Get the most recent market data for multiple tickers efficiently.

        Uses DISTINCT ON to avoid N+1 queries and returns MarketData objects.

        Args:
            ticker_ids: List of ticker IDs

        Returns:
            Dictionary mapping ticker_id to most recent MarketData object
        """
        if not ticker_ids:
            return {}

        async with self._session_factory() as session:
            # Use SQLAlchemy ORM query with DISTINCT ON
            result = await session.execute(
                select(MarketData)
                .where(MarketData.ticker_id.in_(ticker_ids))
                .distinct(MarketData.ticker_id)
                .order_by(MarketData.ticker_id, MarketData.date.desc())
            )
            
            market_data_list = result.scalars().all()

            # Convert to dict mapping ticker_id -> MarketData
            result_dict: Dict[UUID, MarketData] = {
                md.ticker_id: md for md in market_data_list
            }

            return result_dict

    async def get_aggregated(
        self,
        ticker_id: UUID,
        interval: str = "1W",
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[AggregatedData]:
        """
        Get aggregated OHLCV data for a ticker by time interval.

        Uses PostgreSQL DATE_TRUNC for efficient server-side aggregation.
        Supports aggregation by day (1D), week (1W), or month (1M).

        Args:
            ticker_id: The ticker ID
            interval: Aggregation interval ("1D", "1W", "1M")
            start: Optional start date
            end: Optional end date

        Returns:
            List of AggregatedData ordered by period_start
        """
        # Map interval to PostgreSQL DATE_TRUNC unit
        trunc_map = {
            "1D": "day",
            "1W": "week",
            "1M": "month",
        }

        if interval not in trunc_map:
            raise ValueError(f"Unsupported interval: {interval}. Use 1D, 1W, or 1M.")

        trunc_unit = trunc_map[interval]

        async with self._session_factory() as session:
            # Build SQL query with DATE_TRUNC for aggregation
            stmt = text(
                """
                SELECT 
                    DATE_TRUNC(:trunc_unit, date)::date AS period_start,
                    (ARRAY_AGG(open ORDER BY date ASC))[1] AS open,
                    MAX(high) AS high,
                    MIN(low) AS low,
                    (ARRAY_AGG(close ORDER BY date DESC))[1] AS close,
                    SUM(volume) AS volume,
                    MAX(date) AS period_end
                FROM market_data
                WHERE ticker_id = :ticker_id
                    AND (:start IS NULL OR date >= :start)
                    AND (:end IS NULL OR date <= :end)
                GROUP BY DATE_TRUNC(:trunc_unit, date)
                ORDER BY period_start ASC
                """
            ).bindparams(
                bindparam("trunc_unit"),
                bindparam("ticker_id"),
                bindparam("start", type_=Date),
                bindparam("end", type_=Date),
            )

            result = await session.execute(
                stmt,
                {
                    "trunc_unit": trunc_unit,
                    "ticker_id": ticker_id,
                    "start": start,
                    "end": end,
                },
            )

            rows = result.all()

            # Convert rows to AggregatedData objects
            aggregated_data = [
                AggregatedData(
                    period_start=row[0],
                    period_end=row[6],
                    open=row[1],
                    high=row[2],
                    low=row[3],
                    close=row[4],
                    volume=row[5],
                    interval=interval,
                )
                for row in rows
            ]

            return aggregated_data
