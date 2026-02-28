"""
Unit tests for TASK 3.11 — Cursor-based Pagination.

Tests cover:
- encode_cursor / decode_cursor round-trip
- decode_cursor error handling (invalid input)
- CursorPagination dataclass validation
- PaginatedResult properties (has_more, total_in_page)
- apply_cursor_pagination SQLAlchemy helper (NEXT/PREV with/without cursor)
- MarketDataRepository.get_history_paginated() via mock session
- API endpoint GET /api/market/history/{ticker}/paginated

Strategy
--------
- All tests are pure unit tests; no real DB or network required.
- SQLAlchemy query building is tested by inspecting compiled SQL strings.
- Repository method is tested by mocking the async session factory.
- API endpoint is tested with FastAPI TestClient and mocked repository.
"""

from __future__ import annotations

import json
import base64
from datetime import date
from decimal import Decimal
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select

from src.shared.repositories.pagination import (
    CursorPagination,
    Direction,
    PaginatedResult,
    decode_cursor,
    encode_cursor,
    apply_cursor_pagination,
)


# ============================================================================
# encode_cursor / decode_cursor
# ============================================================================


class TestEncodeCursor:
    """Verify cursor encoding."""

    def test_encode_returns_string(self):
        result = encode_cursor({"date": "2026-01-15"})
        assert isinstance(result, str)

    def test_encode_is_url_safe_base64(self):
        """Encoded cursor must not contain '+', '/', or '=' (URL-safe, no padding)."""
        result = encode_cursor({"date": "2026-01-15"})
        assert "+" not in result
        assert "/" not in result
        assert "=" not in result

    def test_encode_round_trips(self):
        """encode → decode must return original dict."""
        original = {"date": "2026-01-15"}
        assert decode_cursor(encode_cursor(original)) == original

    def test_encode_multiple_keys(self):
        original = {"date": "2026-01-15", "id": "abc123"}
        assert decode_cursor(encode_cursor(original)) == original

    def test_encode_opaque_to_casual_inspection(self):
        """Raw cursor string should not look like a plain date."""
        cursor = encode_cursor({"date": "2026-01-15"})
        assert "2026" not in cursor  # not readable as plain text


class TestDecodeCursor:
    """Verify cursor decoding and error handling."""

    def test_decode_valid(self):
        cursor = encode_cursor({"date": "2026-01-01"})
        result = decode_cursor(cursor)
        assert result == {"date": "2026-01-01"}

    def test_decode_invalid_base64_raises(self):
        with pytest.raises(ValueError, match="Invalid cursor"):
            decode_cursor("!!!not-base64!!!")

    def test_decode_valid_base64_but_invalid_json_raises(self):
        # Encode raw bytes that are valid base64 but not JSON
        bad = base64.urlsafe_b64encode(b"not json at all").rstrip(b"=").decode()
        with pytest.raises(ValueError, match="Invalid cursor"):
            decode_cursor(bad)

    def test_decode_with_padding_stripped(self):
        """decode_cursor must handle cursors that lost their base64 padding."""
        original = {"date": "2026-12-31"}
        cursor = encode_cursor(original)
        # Strip any existing padding (already done by encode_cursor)
        # and add one extraneous character to force re-padding
        result = decode_cursor(cursor)
        assert result == original


# ============================================================================
# CursorPagination dataclass
# ============================================================================


class TestCursorPagination:
    """Verify CursorPagination validation."""

    def test_default_values(self):
        p = CursorPagination()
        assert p.limit == 50
        assert p.cursor is None
        assert p.direction == Direction.NEXT

    def test_custom_limit(self):
        p = CursorPagination(limit=100)
        assert p.limit == 100

    def test_direction_from_string(self):
        """direction can be provided as a plain string."""
        p = CursorPagination(direction="prev")
        assert p.direction == Direction.PREV

    def test_limit_too_low_raises(self):
        with pytest.raises(ValueError, match="limit must be between"):
            CursorPagination(limit=0)

    def test_limit_too_high_raises(self):
        with pytest.raises(ValueError, match="limit must be between"):
            CursorPagination(limit=501)

    def test_limit_boundary_low(self):
        p = CursorPagination(limit=1)
        assert p.limit == 1

    def test_limit_boundary_high(self):
        p = CursorPagination(limit=500)
        assert p.limit == 500


# ============================================================================
# PaginatedResult properties
# ============================================================================


class TestPaginatedResult:
    """Verify PaginatedResult properties."""

    def test_has_more_true_when_next_cursor_set(self):
        r = PaginatedResult(items=["a"], next_cursor="abc", prev_cursor=None)
        assert r.has_more is True

    def test_has_more_false_when_next_cursor_none(self):
        r = PaginatedResult(items=["a"], next_cursor=None, prev_cursor=None)
        assert r.has_more is False

    def test_total_in_page(self):
        r = PaginatedResult(items=["a", "b", "c"])
        assert r.total_in_page == 3

    def test_empty_result(self):
        r = PaginatedResult()
        assert r.has_more is False
        assert r.total_in_page == 0
        assert r.next_cursor is None
        assert r.prev_cursor is None


# ============================================================================
# apply_cursor_pagination SQLAlchemy helper
# ============================================================================


def _compile(stmt) -> str:
    """Compile a SQLAlchemy statement to raw SQL string (dialect-agnostic)."""
    from sqlalchemy.dialects import postgresql
    return str(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


class _FakeModel:
    """Minimal stand-in for a SQLAlchemy model with a date column."""
    from sqlalchemy import Column, Date

    date = Column("date", Date)


from sqlalchemy import Table, Column, Date, MetaData
from sqlalchemy.orm import DeclarativeBase


class _Base(DeclarativeBase):
    pass


class _FakeRow(_Base):
    __tablename__ = "fake"
    __table_args__ = {"extend_existing": True}
    from sqlalchemy import Integer
    id = Column(Integer, primary_key=True)
    date = Column(Date)


class TestApplyCursorPagination:
    """Verify the SQL produced by apply_cursor_pagination."""

    def _base_query(self):
        return select(_FakeRow)

    def test_next_no_cursor_order_asc(self):
        pagination = CursorPagination(limit=10, cursor=None, direction=Direction.NEXT)
        stmt = apply_cursor_pagination(self._base_query(), pagination, _FakeRow.date, cursor_value=None)
        sql = _compile(stmt)
        assert "ORDER BY fake.date ASC" in sql
        assert "LIMIT 11" in sql
        # No cursor WHERE clause
        assert "fake.date >" not in sql

    def test_next_with_cursor_adds_where(self):
        cursor_date = date(2026, 1, 15)
        pagination = CursorPagination(limit=10, direction=Direction.NEXT)
        stmt = apply_cursor_pagination(self._base_query(), pagination, _FakeRow.date, cursor_value=cursor_date)
        sql = _compile(stmt)
        assert "fake.date > '2026-01-15'" in sql
        assert "ORDER BY fake.date ASC" in sql
        assert "LIMIT 11" in sql

    def test_prev_no_cursor_order_desc(self):
        pagination = CursorPagination(limit=5, cursor=None, direction=Direction.PREV)
        stmt = apply_cursor_pagination(self._base_query(), pagination, _FakeRow.date, cursor_value=None)
        sql = _compile(stmt)
        assert "ORDER BY fake.date DESC" in sql
        assert "LIMIT 6" in sql

    def test_prev_with_cursor_adds_lt_where(self):
        cursor_date = date(2026, 6, 1)
        pagination = CursorPagination(limit=5, direction=Direction.PREV)
        stmt = apply_cursor_pagination(self._base_query(), pagination, _FakeRow.date, cursor_value=cursor_date)
        sql = _compile(stmt)
        assert "fake.date < '2026-06-01'" in sql
        assert "ORDER BY fake.date DESC" in sql

    def test_limit_is_incremented_by_one(self):
        """apply_cursor_pagination always fetches limit+1 to detect has_more."""
        pagination = CursorPagination(limit=20)
        stmt = apply_cursor_pagination(self._base_query(), pagination, _FakeRow.date, cursor_value=None)
        sql = _compile(stmt)
        assert "LIMIT 21" in sql


# ============================================================================
# MarketDataRepository.get_history_paginated() — business logic
# ============================================================================


def _make_md(d: date) -> MagicMock:
    """Build a MagicMock that looks like a MarketData row with the given date."""
    md = MagicMock()
    md.date = d
    md.open = Decimal("100.00")
    md.high = Decimal("110.00")
    md.low = Decimal("90.00")
    md.close = Decimal("105.00")
    md.volume = 1_000_000
    return md


def _make_repo_with_rows(rows: list):
    """Build a MarketDataRepository whose DB always returns ``rows``."""
    from src.market_data.repositories.market_data_repository import MarketDataRepository

    # Build a mock session that returns ``rows`` from scalars().all()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = rows

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session)
    return MarketDataRepository(session_factory=mock_factory)


class TestGetHistoryPaginated:
    """Unit tests for the repository method."""

    @pytest.mark.asyncio
    async def test_empty_dataset_returns_empty_result(self):
        repo = _make_repo_with_rows([])
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=10),
        )
        assert result.items == []
        assert result.next_cursor is None
        assert result.prev_cursor is None
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_first_page_no_cursor(self):
        """First page: no cursor, direction NEXT, 5 rows, limit 3 → has_more True."""
        rows = [_make_md(date(2026, 1, i)) for i in range(1, 6)]  # 5 rows
        # Repo will fetch limit+1 = 4; simulate returning 4
        repo = _make_repo_with_rows(rows[:4])
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=3),
        )
        assert len(result.items) == 3
        assert result.has_more is True
        assert result.next_cursor is not None
        assert result.prev_cursor is None  # first page → no prev

    @pytest.mark.asyncio
    async def test_last_page_no_has_more(self):
        """Last page: fewer rows than limit → has_more False."""
        rows = [_make_md(date(2026, 1, i)) for i in range(1, 3)]  # 2 rows
        repo = _make_repo_with_rows(rows)  # only 2, limit=5 → no extra row
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=5),
        )
        assert result.has_more is False
        assert result.next_cursor is None

    @pytest.mark.asyncio
    async def test_next_cursor_encodes_last_item_date(self):
        rows = [_make_md(date(2026, 1, i)) for i in range(1, 6)]
        repo = _make_repo_with_rows(rows[:4])  # 4 rows → has_more True, items = first 3
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=3),
        )
        decoded = decode_cursor(result.next_cursor)
        assert decoded["date"] == date(2026, 1, 3).isoformat()

    @pytest.mark.asyncio
    async def test_prev_cursor_set_when_cursor_provided(self):
        """When a cursor is given (not first page), prev_cursor must be set."""
        cursor = encode_cursor({"date": "2026-01-03"})
        rows = [_make_md(date(2026, 1, i)) for i in range(4, 8)]  # 4 rows, limit 3 → extra
        repo = _make_repo_with_rows(rows)
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=3, cursor=cursor, direction=Direction.NEXT),
        )
        assert result.prev_cursor is not None
        decoded = decode_cursor(result.prev_cursor)
        assert decoded["date"] == date(2026, 1, 4).isoformat()  # first item returned

    @pytest.mark.asyncio
    async def test_prev_direction_reverses_order(self):
        """PREV query returns rows in DESC order; result must be re-sorted ASC."""
        # Simulate DB returning rows in DESC order (as the query would produce)
        desc_rows = [_make_md(date(2026, 1, i)) for i in range(5, 1, -1)]  # 4 rows, DESC
        repo = _make_repo_with_rows(desc_rows[:3])  # limit=3, no extra → no more prev
        cursor = encode_cursor({"date": "2026-01-06"})
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=3, cursor=cursor, direction=Direction.PREV),
        )
        # Items must be in ascending order after reversal
        dates = [item.date for item in result.items]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_invalid_cursor_raises(self):
        """An invalid cursor string should raise ValueError."""
        repo = _make_repo_with_rows([])
        with pytest.raises(ValueError):
            await repo.get_history_paginated(
                ticker_id=uuid4(),
                pagination=CursorPagination(limit=10, cursor="!!!invalid!!!"),
            )

    @pytest.mark.asyncio
    async def test_cursor_missing_date_key_raises(self):
        """Cursor without 'date' key should raise ValueError."""
        bad_cursor = encode_cursor({"wrong_key": "2026-01-01"})
        repo = _make_repo_with_rows([])
        with pytest.raises(ValueError, match="date"):
            await repo.get_history_paginated(
                ticker_id=uuid4(),
                pagination=CursorPagination(limit=10, cursor=bad_cursor),
            )

    @pytest.mark.asyncio
    async def test_single_page_dataset(self):
        """Dataset exactly fitting one page: no cursors."""
        rows = [_make_md(date(2026, 1, i)) for i in range(1, 4)]  # 3 rows, limit 3
        repo = _make_repo_with_rows(rows)  # exactly 3, no extra row
        result = await repo.get_history_paginated(
            ticker_id=uuid4(),
            pagination=CursorPagination(limit=3),
        )
        assert len(result.items) == 3
        assert result.has_more is False
        assert result.next_cursor is None
        assert result.prev_cursor is None


# ============================================================================
# API endpoint tests
# ============================================================================

def _build_test_app() -> FastAPI:
    """Build a minimal FastAPI app with only the market data router."""
    from src.market_data.api.routes import router
    app = FastAPI()
    app.include_router(router)
    return app


class TestPaginatedEndpoint:
    """Verify GET /api/market/history/{ticker}/paginated."""

    def _client_with_repo(self, mock_repo) -> TestClient:
        from src.market_data.api.routes import router
        from src.market_data.api.dependencies import get_market_data_repository
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_market_data_repository] = lambda: mock_repo
        return TestClient(app, raise_server_exceptions=True)

    def _mock_repo(self, result: PaginatedResult):
        repo = MagicMock()
        repo.get_history_paginated = AsyncMock(return_value=result)
        return repo

    def test_returns_200_first_page(self):
        rows = [_make_md(date(2026, 1, i)) for i in range(1, 4)]
        result = PaginatedResult(items=rows, next_cursor="abc", prev_cursor=None)
        repo = self._mock_repo(result)

        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/AAPL/paginated")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["items"]) == 3
        assert data["next_cursor"] == "abc"
        assert data["prev_cursor"] is None
        assert data["has_more"] is True

    def test_returns_404_for_unknown_ticker(self):
        from fastapi import HTTPException

        async def raise_404(*args, **kwargs):
            raise HTTPException(status_code=404, detail="not found")

        repo = MagicMock()
        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(side_effect=HTTPException(status_code=404, detail="not found")),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/UNKNOWN/paginated")

        assert resp.status_code == 404

    def test_returns_400_for_invalid_cursor(self):
        repo = MagicMock()
        repo.get_history_paginated = AsyncMock(side_effect=ValueError("Invalid cursor"))

        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/AAPL/paginated?cursor=!!!bad!!!")

        assert resp.status_code == 400

    def test_returns_400_for_invalid_date_range(self):
        repo = MagicMock()
        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get(
                "/api/market/history/AAPL/paginated"
                "?start_date=2026-12-31&end_date=2026-01-01"
            )
        assert resp.status_code == 400

    def test_empty_dataset_returns_200(self):
        result = PaginatedResult(items=[], next_cursor=None, prev_cursor=None)
        repo = self._mock_repo(result)

        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/AAPL/paginated")

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["items"] == []
        assert data["has_more"] is False

    def test_direction_prev_accepted(self):
        cursor = encode_cursor({"date": "2026-03-01"})
        result = PaginatedResult(items=[], next_cursor=None, prev_cursor=None)
        repo = self._mock_repo(result)

        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get(
                f"/api/market/history/AAPL/paginated?cursor={cursor}&direction=prev"
            )

        assert resp.status_code == 200

    def test_limit_out_of_range_rejected(self):
        """limit=0 should be rejected by FastAPI query validation (422)."""
        repo = MagicMock()
        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/AAPL/paginated?limit=0")
        assert resp.status_code == 422

    def test_response_schema_fields_present(self):
        rows = [_make_md(date(2026, 2, 1))]
        result = PaginatedResult(items=rows, next_cursor=None, prev_cursor=None)
        repo = self._mock_repo(result)

        with patch(
            "src.market_data.api.routes._resolve_ticker_id",
            new=AsyncMock(return_value=uuid4()),
        ):
            client = self._client_with_repo(repo)
            resp = client.get("/api/market/history/AAPL/paginated?limit=10")

        data = resp.json()["data"]
        for field in ("symbol", "items", "next_cursor", "prev_cursor", "has_more",
                      "total_in_page", "limit"):
            assert field in data, f"Missing field: {field}"
        assert data["limit"] == 10
