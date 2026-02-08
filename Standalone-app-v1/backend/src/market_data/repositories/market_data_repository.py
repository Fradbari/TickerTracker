"""Repository for MarketData data access."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, insert, select, text, update
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

        Uses window function to avoid N+1 queries.

        Args:
            ticker_ids: List of ticker IDs

        Returns:
            Dictionary mapping ticker_id to most recent MarketData
        """
        if not ticker_ids:
            return {}

        async with self._session_factory() as session:
            # Use window function to get latest for each ticker
            stmt = text(
                """
                SELECT DISTINCT ON (ticker_id) *
                FROM market_data
                WHERE ticker_id = ANY(:ticker_ids)
                ORDER BY ticker_id, date DESC
                """
            )

            result = await session.execute(
                stmt.bindparams(ticker_ids=ticker_ids)
            )
            rows = result.all()

            # Convert to dict mapping
            result_dict: Dict[UUID, MarketData] = {}
            for row in rows:
                ticker_id = row[1]  # ticker_id column position
                result_dict[ticker_id] = row

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

        Supports aggregation by day (1D), week (1W), or month (1M).

        Args:
            ticker_id: The ticker ID
            interval: Aggregation interval ("1D", "1W", "1M")
            start: Optional start date
            end: Optional end date

        Returns:
            List of AggregatedData ordered by period_start
        """
        # Fetch all data for the ticker
        history = await self.get_history(
            ticker_id,
            start or date(2000, 1, 1),
            end or date.today(),
        )

        if not history:
            return []

        # Aggregate based on interval
        if interval == "1D":
            return self._aggregate_by_day(history, interval)
        elif interval == "1W":
            return self._aggregate_by_week(history, interval)
        elif interval == "1M":
            return self._aggregate_by_month(history, interval)
        else:
            raise ValueError(f"Unsupported interval: {interval}")

    def _aggregate_by_day(
        self, data: List[MarketData], interval: str
    ) -> List[AggregatedData]:
        """Aggregate OHLCV data by calendar day."""
        aggregated: Dict[date, AggregatedData] = {}

        for md in data:
            if md.date not in aggregated:
                aggregated[md.date] = AggregatedData(
                    period_start=md.date,
                    period_end=md.date,
                    open=md.open,
                    high=md.high,
                    low=md.low,
                    close=md.close,
                    volume=md.volume,
                    interval=interval,
                )
            else:
                agg = aggregated[md.date]
                agg.high = max(agg.high, md.high)
                agg.low = min(agg.low, md.low)
                agg.close = md.close
                agg.volume += md.volume

        return sorted(aggregated.values(), key=lambda x: x.period_start)

    def _aggregate_by_week(
        self, data: List[MarketData], interval: str
    ) -> List[AggregatedData]:
        """Aggregate OHLCV data by ISO week."""
        aggregated: Dict[tuple, AggregatedData] = {}

        for md in data:
            iso_calendar = md.date.isocalendar()
            week_key = (iso_calendar[0], iso_calendar[1])  # (year, week)

            if week_key not in aggregated:
                aggregated[week_key] = AggregatedData(
                    period_start=md.date,
                    period_end=md.date,
                    open=md.open,
                    high=md.high,
                    low=md.low,
                    close=md.close,
                    volume=md.volume,
                    interval=interval,
                )
            else:
                agg = aggregated[week_key]
                agg.period_end = md.date
                agg.high = max(agg.high, md.high)
                agg.low = min(agg.low, md.low)
                agg.close = md.close
                agg.volume += md.volume

        return sorted(aggregated.values(), key=lambda x: x.period_start)

    def _aggregate_by_month(
        self, data: List[MarketData], interval: str
    ) -> List[AggregatedData]:
        """Aggregate OHLCV data by calendar month."""
        aggregated: Dict[tuple, AggregatedData] = {}

        for md in data:
            month_key = (md.date.year, md.date.month)

            if month_key not in aggregated:
                aggregated[month_key] = AggregatedData(
                    period_start=md.date,
                    period_end=md.date,
                    open=md.open,
                    high=md.high,
                    low=md.low,
                    close=md.close,
                    volume=md.volume,
                    interval=interval,
                )
            else:
                agg = aggregated[month_key]
                agg.period_end = md.date
                agg.high = max(agg.high, md.high)
                agg.low = min(agg.low, md.low)
                agg.close = md.close
                agg.volume += md.volume

        return sorted(aggregated.values(), key=lambda x: x.period_start)
