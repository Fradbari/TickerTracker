"""
Cursor-based pagination utilities (TASK 3.11).

Provides opaque cursor pagination for large datasets with O(1) page
performance regardless of page number — unlike OFFSET-based pagination
where cost grows linearly with page depth.

Cursor format
-------------
A cursor is a **base64url-encoded JSON object** that contains the value(s)
of the sort column(s) at the boundary of a page.  Being opaque to clients
prevents manual manipulation while remaining easy to pass as a query
parameter.

Example cursor payload (before encoding):
    {"date": "2026-01-15"}

Encoded cursor (URL-safe base64, no padding):
    "eyJkYXRlIjogIjIwMjYtMDEtMTUifQ"

Usage
-----
    # Build pagination request
    pagination = CursorPagination(limit=50, cursor=request_cursor, direction=Direction.NEXT)

    # In repository
    result: PaginatedResult[MarketData] = await repo.get_history_paginated(
        ticker_id=tid,
        pagination=pagination,
        start=date(2025, 1, 1),
        end=date(2026, 1, 1),
    )

    # Consume result
    for item in result.items:
        ...
    if result.has_more:
        next_cursor = result.next_cursor  # pass to next request

Limitations
-----------
- Sort column(s) must form a unique key (or be combined with a tie-breaker)
  to guarantee stable pagination across concurrent writes.
- Jumping to an arbitrary page number is not directly supported; clients
  must navigate forward/backward sequentially.
- The ``start``/``end`` date filters narrow the navigable window; the cursor
  must fall within that window.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------


class Direction(str, Enum):
    """Pagination direction."""

    NEXT = "next"
    PREV = "prev"


# ---------------------------------------------------------------------------
# Input / Output dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CursorPagination:
    """
    Input parameters for a cursor-paginated query.

    Attributes:
        limit:     Maximum number of items to return per page (1–500).
        cursor:    Opaque cursor string from a previous response.
                   ``None`` indicates the first page.
        direction: Whether to paginate forward (NEXT) or backward (PREV).
                   Defaults to NEXT.
    """

    limit: int = 50
    cursor: str | None = None
    direction: Direction = Direction.NEXT

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= 500:
            raise ValueError(f"limit must be between 1 and 500, got {self.limit}")
        if isinstance(self.direction, str):
            self.direction = Direction(self.direction)


@dataclass
class PaginatedResult(Generic[T]):
    """
    Output of a cursor-paginated query.

    Attributes:
        items:       The (up to ``limit``) items for the current page,
                     always in ascending sort order.
        next_cursor: Opaque cursor to pass with ``direction=NEXT`` to get
                     the page after the current one.  ``None`` if this is
                     the last page.
        prev_cursor: Opaque cursor to pass with ``direction=PREV`` to get
                     the page before the current one.  ``None`` if this is
                     the first page.
        has_more:    Shorthand flag — ``True`` when ``next_cursor`` is not
                     ``None`` (there are more items in the forward direction).
        total_in_page: Number of items in this page.
    """

    items: list[T] = field(default_factory=list)
    next_cursor: str | None = None
    prev_cursor: str | None = None

    @property
    def has_more(self) -> bool:
        """True when there are more pages in the NEXT direction."""
        return self.next_cursor is not None

    @property
    def total_in_page(self) -> int:
        """Number of items in the current page."""
        return len(self.items)


# ---------------------------------------------------------------------------
# Cursor encode / decode
# ---------------------------------------------------------------------------


def encode_cursor(values: dict) -> str:
    """
    Encode a dict of sort-column values into an opaque cursor string.

    The result is URL-safe base64 (no padding) so it can be used directly
    in query parameters without additional URL encoding.

    Args:
        values: Dict mapping column name to its scalar value.
                Values that are not natively JSON-serialisable (e.g. ``date``)
                should be converted to strings before calling this function.

    Returns:
        Opaque base64url string.

    Example:
        >>> encode_cursor({"date": "2026-01-15"})
        'eyJkYXRlIjogIjIwMjYtMDEtMTUifQ'
    """
    payload = json.dumps(values, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()


def decode_cursor(cursor: str) -> dict:
    """
    Decode an opaque cursor string back into a dict.

    Args:
        cursor: The cursor string returned by ``encode_cursor``.

    Returns:
        Dict of sort-column values.

    Raises:
        ValueError: If the cursor is not valid base64 or not valid JSON.

    Example:
        >>> decode_cursor('eyJkYXRlIjogIjIwMjYtMDEtMTUifQ')
        {'date': '2026-01-15'}
    """
    try:
        # Re-add stripped base64 padding
        padded = cursor + "=" * (-len(cursor) % 4)
        decoded = base64.urlsafe_b64decode(padded).decode()
        return json.loads(decoded)
    except Exception as exc:
        raise ValueError(f"Invalid cursor: {exc}") from exc


# ---------------------------------------------------------------------------
# SQLAlchemy helper
# ---------------------------------------------------------------------------


def apply_cursor_pagination(query, pagination: CursorPagination, sort_column, cursor_value=None):
    """
    Apply cursor-based pagination constraints to a SQLAlchemy select statement.

    This helper applies:
    1. The cursor WHERE condition (``sort_column > cursor_value`` for NEXT,
       ``sort_column < cursor_value`` for PREV) when ``cursor_value`` is not None.
    2. The ORDER BY direction appropriate for the navigation direction.
    3. A LIMIT of ``pagination.limit + 1`` (to detect whether more pages
       exist without a separate COUNT query).

    The caller is responsible for decoding the cursor string and converting
    it to the correct Python type (e.g., ``date``) before passing it as
    ``cursor_value``.

    Args:
        query:        A SQLAlchemy ``select()`` statement already filtered by
                      any caller-side WHERE clauses (e.g. ticker_id, start,
                      end date).
        pagination:   :class:`CursorPagination` instance with the cursor,
                      limit, and direction.  Its ``cursor`` field is ignored
                      here — use ``cursor_value`` instead.
        sort_column:  The SQLAlchemy ORM column expression to sort/paginate by
                      (e.g. ``MarketData.date``).
        cursor_value: The already-decoded, type-correct value to compare in the
                      WHERE clause.  Pass ``None`` to get the first/last page
                      without a cursor condition.

    Returns:
        Modified SQLAlchemy statement with cursor condition, ORDER BY, and
        LIMIT applied.

    Notes:
        - For NEXT direction with ``cursor_value=None`` the query returns the
          first page (oldest / smallest values first).
        - For PREV direction with ``cursor_value=None`` the query returns the
          last page (newest / largest values first).
        - The returned query fetches ``limit + 1`` rows.  Callers must slice
          to ``limit`` items and use the extra row only to set ``has_more``.

    Example::

        from datetime import date
        from src.shared.repositories.pagination import (
            CursorPagination, Direction, apply_cursor_pagination, decode_cursor,
        )

        # Decode cursor and extract sort value
        cursor_date = None
        if pagination.cursor:
            cursor_date = date.fromisoformat(decode_cursor(pagination.cursor)["date"])

        base_q = select(MarketData).where(MarketData.ticker_id == tid)
        paged_q = apply_cursor_pagination(base_q, pagination, MarketData.date, cursor_date)
        rows = (await session.execute(paged_q)).scalars().all()
    """
    fetch_limit = pagination.limit + 1  # extra row to detect has_more

    if pagination.direction == Direction.NEXT:
        if cursor_value is not None:
            query = query.where(sort_column > cursor_value)
        query = query.order_by(sort_column.asc()).limit(fetch_limit)
    else:  # PREV
        if cursor_value is not None:
            query = query.where(sort_column < cursor_value)
        query = query.order_by(sort_column.desc()).limit(fetch_limit)

    return query
