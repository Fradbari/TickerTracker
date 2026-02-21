"""
Unit tests for Data Lineage module — TASK 3.9

Tests cover:
- DataSource enum and from_legacy() conversion
- LineageTracked.compute_quality_score() logic
- MarketData inherits lineage fields from mixin
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from src.shared.domain.lineage import DataSource, LineageTracked
from src.market_data.domain.market_data import MarketData


# ---------------------------------------------------------------------------
# DataSource enum — from_legacy()
# ---------------------------------------------------------------------------


class TestDataSourceFromLegacy:
    """Tests for DataSource.from_legacy() mapping."""

    def test_data_source_from_legacy_yahoo(self):
        """Legacy 'yahoo' string maps to YAHOO_FINANCE enum value."""
        result = DataSource.from_legacy("yahoo")
        assert result == DataSource.YAHOO_FINANCE
        assert result.value == "yahoo_finance"

    def test_data_source_from_legacy_yahoo_finance(self):
        """Already-canonical 'yahoo_finance' string maps to YAHOO_FINANCE."""
        result = DataSource.from_legacy("yahoo_finance")
        assert result == DataSource.YAHOO_FINANCE

    def test_data_source_from_legacy_manual(self):
        """Legacy 'manual' string maps to MANUAL_ENTRY enum value."""
        result = DataSource.from_legacy("manual")
        assert result == DataSource.MANUAL_ENTRY
        assert result.value == "manual_entry"

    def test_data_source_from_legacy_manual_entry(self):
        """Already-canonical 'manual_entry' string maps to MANUAL_ENTRY."""
        result = DataSource.from_legacy("manual_entry")
        assert result == DataSource.MANUAL_ENTRY

    def test_data_source_from_legacy_finnhub(self):
        """'finnhub' string maps to FINNHUB enum value."""
        result = DataSource.from_legacy("finnhub")
        assert result == DataSource.FINNHUB

    def test_data_source_unknown_defaults_to_yahoo(self):
        """Unknown strings default to YAHOO_FINANCE."""
        result = DataSource.from_legacy("some_unknown_source")
        assert result == DataSource.YAHOO_FINANCE

    def test_data_source_from_legacy_case_insensitive(self):
        """Mapping is case-insensitive via .lower()."""
        result = DataSource.from_legacy("YAHOO")
        assert result == DataSource.YAHOO_FINANCE

    def test_data_source_str_mixin(self):
        """DataSource is a str subclass — can be used as a plain string."""
        assert DataSource.YAHOO_FINANCE == "yahoo_finance"
        assert isinstance(DataSource.YAHOO_FINANCE, str)


# ---------------------------------------------------------------------------
# LineageTracked.compute_quality_score()
# ---------------------------------------------------------------------------


class TestComputeQualityScore:
    """Tests for LineageTracked.compute_quality_score() scoring formula."""

    def _make_obj(self) -> LineageTracked:
        """Instantiate a bare LineageTracked object for direct method calls."""
        obj = LineageTracked.__new__(LineageTracked)
        return obj

    def test_compute_quality_score_fresh_data(self):
        """Fresh data (source_ts = now) with full OHLCV → score >= 0.80."""
        obj = self._make_obj()
        source_ts = datetime.utcnow()
        score = obj.compute_quality_score(
            source_ts=source_ts,
            has_volume=True,
            has_ohlc=True,
        )
        # freshness=1.00 * 0.6 + completeness=0.80 * 0.4 = 0.60 + 0.32 = 0.92
        assert score >= Decimal("0.80")
        assert score <= Decimal("1.00")

    def test_compute_quality_score_stale_data(self):
        """Stale data (30 days ago) → score lower than fresh data."""
        obj = self._make_obj()
        source_ts = datetime.utcnow() - timedelta(days=30)
        score = obj.compute_quality_score(
            source_ts=source_ts,
            has_volume=True,
            has_ohlc=True,
        )
        # freshness=0.50 * 0.6 + completeness=0.80 * 0.4 = 0.30 + 0.32 = 0.62
        # Must be less than fresh score (0.92) and below 0.65
        assert score < Decimal("0.65")
        assert score >= Decimal("0.00")

    def test_compute_quality_score_missing_volume(self):
        """Missing volume (has_volume=False) reduces score compared to full data."""
        obj = self._make_obj()
        source_ts = datetime.utcnow()  # Fresh data

        score_full = obj.compute_quality_score(
            source_ts=source_ts,
            has_volume=True,
            has_ohlc=True,
        )
        score_no_vol = obj.compute_quality_score(
            source_ts=source_ts,
            has_volume=False,
            has_ohlc=True,
        )
        # Missing volume reduces completeness by 0.10, so score_no_vol < score_full
        assert score_no_vol < score_full
        # freshness=1.00 * 0.6 + (0.80 - 0.10) * 0.4 = 0.60 + 0.28 = 0.88
        assert score_no_vol == Decimal("0.88")

    def test_compute_quality_score_missing_ohlc(self):
        """Missing OHLC (has_ohlc=False) reduces score significantly."""
        obj = self._make_obj()
        source_ts = datetime.utcnow()

        score = obj.compute_quality_score(
            source_ts=source_ts,
            has_volume=True,
            has_ohlc=False,
        )
        # freshness=1.00 * 0.6 + (0.80 - 0.40) * 0.4 = 0.60 + 0.16 = 0.76
        assert score == Decimal("0.76")

    def test_compute_quality_score_no_source_ts(self):
        """No source_ts → freshness defaults to 0.50."""
        obj = self._make_obj()
        score = obj.compute_quality_score(
            source_ts=None,
            has_volume=True,
            has_ohlc=True,
        )
        # freshness=0.50 * 0.6 + completeness=0.80 * 0.4 = 0.30 + 0.32 = 0.62
        assert score == Decimal("0.62")

    def test_compute_quality_score_clamped_to_one(self):
        """Score is clamped to [0.00, 1.00] — never exceeds 1.00."""
        obj = self._make_obj()
        score = obj.compute_quality_score(
            source_ts=datetime.utcnow(),
            has_volume=True,
            has_ohlc=True,
        )
        assert score <= Decimal("1.00")

    def test_compute_quality_score_returns_decimal(self):
        """The return type is always Decimal."""
        obj = self._make_obj()
        result = obj.compute_quality_score()
        assert isinstance(result, Decimal)


# ---------------------------------------------------------------------------
# MarketData mixin integration
# ---------------------------------------------------------------------------


class TestMarketDataInheritsLineage:
    """Verify MarketData correctly inherits LineageTracked mixin."""

    def test_market_data_inherits_mixin(self):
        """MarketData class is a subclass of LineageTracked."""
        assert issubclass(MarketData, LineageTracked)

    def test_lineage_mixin_fields_exist(self):
        """MarketData has all four lineage columns from the mixin."""
        # Check via SQLAlchemy column introspection
        mapper = MarketData.__mapper__
        column_names = {col.key for col in mapper.column_attrs}

        assert "data_source" in column_names, "data_source column missing"
        assert "source_timestamp" in column_names, "source_timestamp column missing"
        assert "ingestion_timestamp" in column_names, "ingestion_timestamp column missing"
        assert "quality_score" in column_names, "quality_score column missing"

    def test_market_data_does_not_have_ingested_at(self):
        """The old ingested_at column is gone — replaced by ingestion_timestamp."""
        mapper = MarketData.__mapper__
        column_names = {col.key for col in mapper.column_attrs}
        assert "ingested_at" not in column_names

    def test_market_data_has_source_timestamp(self):
        """source_timestamp column exists and is nullable (new in TASK 3.9)."""
        mapper = MarketData.__mapper__
        col = mapper.columns.get("source_timestamp")
        assert col is not None
        assert col.nullable is True

    def test_market_data_has_compute_quality_score(self):
        """MarketData inherits compute_quality_score() method from mixin."""
        assert hasattr(MarketData, "compute_quality_score")
        assert callable(MarketData.compute_quality_score)
