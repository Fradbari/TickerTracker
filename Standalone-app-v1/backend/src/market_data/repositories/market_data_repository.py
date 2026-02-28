"""Repository for MarketData data access."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from src.shared.domain.lineage import DataSource
from src.shared.repositories.pagination import (
    CursorPagination,
    Direction,
    PaginatedResult,
    decode_cursor,
    encode_cursor,
)

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
        data_source: str = DataSource.YAHOO_FINANCE.value,
        quality_score: Optional[Decimal] = None,
        source_timestamp: Optional[datetime] = None,
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
        self.source_timestamp = source_timestamp


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
                        "source_timestamp": row.source_timestamp,
                        "ingestion_timestamp": func.now(),
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
                        MarketData.source_timestamp: stmt.excluded.source_timestamp,
                        MarketData.ingestion_timestamp: func.now(),
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

    async def get_history_paginated(
        self,
        ticker_id: UUID,
        pagination: CursorPagination,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> PaginatedResult[MarketData]:
        """
        Get historical market data using cursor-based pagination (TASK 3.11).

        Returns at most ``pagination.limit`` items per page with O(1) cost
        regardless of page depth, because a cursor (date value) replaces the
        OFFSET clause.

        The cursor encodes the ``date`` column as a string (``YYYY-MM-DD``).
        Clients receive opaque ``next_cursor`` / ``prev_cursor`` values and
        pass them back unchanged with the desired ``direction``.

        Coexistence with start/end filters
        -----------------------------------
        ``start`` and ``end`` behave as a fixed window: only rows within
        [start, end] are ever returned.  The cursor further narrows *within*
        that window to the boundary of the last fetched page.

        Edge cases handled
        ------------------
        - First page (no cursor): prev_cursor = None.
        - Last page (no more rows forward): next_cursor = None.
        - Empty result: returns PaginatedResult with empty items, both cursors None.
        - Dataset smaller than one page: has_more = False, both cursors None.

        Args:
            ticker_id:  Ticker to query.
            pagination: :class:`~src.shared.repositories.pagination.CursorPagination`
                        with limit, optional cursor, and direction.
            start:      Optional lower-bound date filter (inclusive).
            end:        Optional upper-bound date filter (inclusive).

        Returns:
            :class:`~src.shared.repositories.pagination.PaginatedResult` with
            items in **ascending date order** and cursor strings for
            forward/backward navigation.

        Example::

            from src.shared.repositories.pagination import CursorPagination, Direction

            # First page
            first = await repo.get_history_paginated(
                ticker_id=tid,
                pagination=CursorPagination(limit=50),
                start=date(2025, 1, 1),
                end=date(2026, 1, 1),
            )

            # Second page
            if first.has_more:
                second = await repo.get_history_paginated(
                    ticker_id=tid,
                    pagination=CursorPagination(
                        limit=50,
                        cursor=first.next_cursor,
                        direction=Direction.NEXT,
                    ),
                    start=date(2025, 1, 1),
                    end=date(2026, 1, 1),
                )

            # Go back to first page
            back = await repo.get_history_paginated(
                ticker_id=tid,
                pagination=CursorPagination(
                    limit=50,
                    cursor=second.prev_cursor,
                    direction=Direction.PREV,
                ),
                start=date(2025, 1, 1),
                end=date(2026, 1, 1),
            )
        """
        # --- Decode cursor date if present ---
        cursor_date: Optional[date] = None
        if pagination.cursor:
            raw = decode_cursor(pagination.cursor)
            if "date" not in raw:
                raise ValueError("Cursor must contain a 'date' key")
            from datetime import date as date_cls
            cursor_date = date_cls.fromisoformat(raw["date"])

        fetch_limit = pagination.limit + 1  # extra to detect has_more

        async with self._session_factory() as session:
            # --- Build base WHERE ---
            conditions = [MarketData.ticker_id == ticker_id]
            if start is not None:
                conditions.append(MarketData.date >= start)
            if end is not None:
                conditions.append(MarketData.date <= end)

            stmt = select(MarketData).where(and_(*conditions))

            # --- Apply cursor condition and ordering ---
            if pagination.direction == Direction.NEXT:
                if cursor_date is not None:
                    stmt = stmt.where(MarketData.date > cursor_date)
                stmt = stmt.order_by(MarketData.date.asc()).limit(fetch_limit)
            else:  # PREV
                if cursor_date is not None:
                    stmt = stmt.where(MarketData.date < cursor_date)
                stmt = stmt.order_by(MarketData.date.desc()).limit(fetch_limit)

            rows = list((await session.execute(stmt)).scalars().all())

        # --- Detect has_more and trim to limit ---
        if pagination.direction == Direction.NEXT:
            has_more_next = len(rows) > pagination.limit
            items = rows[: pagination.limit] if has_more_next else rows

            next_cursor = (
                encode_cursor({"date": items[-1].date.isoformat()})
                if has_more_next and items
                else None
            )
            # There's a previous page whenever we used a cursor (not the first page)
            prev_cursor = (
                encode_cursor({"date": items[0].date.isoformat()})
                if cursor_date is not None and items
                else None
            )

        else:  # PREV — fetched in DESC order, need to reverse for ASC presentation
            has_more_prev = len(rows) > pagination.limit
            rows = rows[: pagination.limit] if has_more_prev else rows
            items = list(reversed(rows))  # back to ascending order

            prev_cursor = (
                encode_cursor({"date": items[0].date.isoformat()})
                if has_more_prev and items
                else None
            )
            # When going PREV we always came from somewhere forward
            next_cursor = (
                encode_cursor({"date": items[-1].date.isoformat()})
                if items
                else None
            )

        return PaginatedResult(
            items=items,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
        )

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
