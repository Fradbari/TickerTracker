"""Repository for MarketData data access."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, func, insert, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from market_data.domain.market_data import MarketData


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
        Get the most recent market data for multiple tickers (avoids N+1).

        Args:
            ticker_ids: List of ticker IDs

        Returns:
            Dictionary mapping ticker_id to its most recent MarketData

        Example:
            >>> tickers = [uuid1, uuid2, uuid3]
            >>> prices = await repo.get_latest_prices_batch(tickers)
            >>> current_price = prices[uuid1].close
        """
        if not ticker_ids:
            return {}

        async with self._session_factory() as session:
            # Use window function to get most recent per ticker
            stmt = select(MarketData).where(
                MarketData.ticker_id.in_(ticker_ids)
                & (
                    MarketData.date
                    == select(func.max(MarketData.date))
                    .where(MarketData.ticker_id == MarketData.ticker_id)
                    .correlate(MarketData)
                    .scalar_subquery()
                )
            )

            result = await session.execute(stmt)
            rows = result.scalars().all()

            return {row.ticker_id: row for row in rows}

    async def get_aggregated(
        self,
        ticker_id: UUID,
        interval: str = "1W",
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> List[AggregatedData]:
        """
        Get aggregated market data by interval (1D, 1W, 1M).

        Aggregates OHLCV data by specified time interval:
        - 1D: Daily (no aggregation, just filtered)
        - 1W: Weekly (Monday to Friday)
        - 1M: Monthly (calendar month)

        Args:
            ticker_id: The ticker ID
            interval: Aggregation interval ('1D', '1W', or '1M')
            start: Optional start date
            end: Optional end date

        Returns:
            List of AggregatedData sorted by period start date

        Example:
            >>> weekly_data = await repo.get_aggregated(ticker_id, "1W")
            >>> for candle in weekly_data:
            ...     print(f"{candle.period_start}: O={candle.open} C={candle.close}")
        """
        async with self._session_factory() as session:
            # Build base query
            query = select(MarketData).where(MarketData.ticker_id == ticker_id)

            if start:
                query = query.where(MarketData.date >= start)
            if end:
                query = query.where(MarketData.date <= end)

            query = query.order_by(MarketData.date.asc())

            result = await session.execute(query)
            all_data = list(result.scalars().all())

            if not all_data:
                return []

            # Group data by interval
            if interval == "1D":
                return [
                    AggregatedData(
                        period_start=row.date,
                        period_end=row.date,
                        open=row.open,
                        high=row.high,
                        low=row.low,
                        close=row.close,
                        volume=row.volume,
                        interval="1D",
                    )
                    for row in all_data
                ]

            elif interval == "1W":
                return self._aggregate_by_week(all_data)

            elif interval == "1M":
                return self._aggregate_by_month(all_data)

            else:
                raise ValueError(
                    f"Invalid interval: {interval}. Use '1D', '1W', or '1M'"
                )

    def _aggregate_by_week(self, data_rows: List[MarketData]) -> List[AggregatedData]:
        """Aggregate data by calendar week (ISO week)."""
        weeks: Dict[tuple, List[MarketData]] = {}

        for row in data_rows:
            iso_year, iso_week, _ = row.date.isocalendar()
            week_key = (iso_year, iso_week)

            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(row)

        aggregated = []
        for (iso_year, iso_week), week_data in sorted(weeks.items()):
            open_price = week_data[0].open
            close_price = week_data[-1].close
            high_price = max(row.high for row in week_data)
            low_price = min(row.low for row in week_data)
            total_volume = sum(row.volume for row in week_data)

            aggregated.append(
                AggregatedData(
                    period_start=week_data[0].date,
                    period_end=week_data[-1].date,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=total_volume,
                    interval="1W",
                )
            )

        return aggregated

    def _aggregate_by_month(self, data_rows: List[MarketData]) -> List[AggregatedData]:
        """Aggregate data by calendar month."""
        months: Dict[tuple, List[MarketData]] = {}

        for row in data_rows:
            month_key = (row.date.year, row.date.month)

            if month_key not in months:
                months[month_key] = []
            months[month_key].append(row)

        aggregated = []
        for (year, month), month_data in sorted(months.items()):
            open_price = month_data[0].open
            close_price = month_data[-1].close
            high_price = max(row.high for row in month_data)
            low_price = min(row.low for row in month_data)
            total_volume = sum(row.volume for row in month_data)

            aggregated.append(
                AggregatedData(
                    period_start=month_data[0].date,
                    period_end=month_data[-1].date,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=total_volume,
                    interval="1M",
                )
            )

        return aggregated
