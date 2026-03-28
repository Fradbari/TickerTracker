"""
Tests for src/market_data/services/quality_monitor.py  (Task 3.8)
=================================================================

Strategy
--------
- All DB I/O mocked via AsyncMock context managers patched on
  ``src.market_data.services.quality_monitor.AsyncSessionLocal``.
- MarketData / Ticker objects built with plain dataclasses or MagicMock
  (no real ORM / DB required).
- No external service calls.

Coverage (16 tests)
-------------------
Rule function unit tests (4):
  - test_rule_positive_prices_pass
  - test_rule_positive_prices_fail
  - test_rule_no_large_gaps_pass
  - test_rule_no_large_gaps_fail
  - test_rule_daily_change_lt50_pass
  - test_rule_daily_change_lt50_fail
  - test_rule_positive_volume_pass
  - test_rule_positive_volume_fail

DataQualityMonitor integration (4):
  - test_run_checks_empty_data (no rows → empty list)
  - test_run_checks_healthy (all rules pass → empty list)
  - test_run_checks_with_issues (bad data → issues returned)
  - test_run_all_checks_no_tickers
  - test_run_all_checks_with_tickers
  - test_run_all_checks_aggregates_report

QualityIssue dataclass:
  - test_quality_issue_str

Job integration:
  - test_daily_quality_check_job
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.market_data.services.quality_monitor import (
    DEFAULT_RULES,
    DataQualityMonitor,
    QualityIssue,
    _check_daily_change_lt50,
    _check_no_large_gaps,
    _check_positive_prices,
    _check_positive_volume,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_row(
    d: date,
    open_: float = 100.0,
    high: float = 110.0,
    low: float = 90.0,
    close: float = 105.0,
    volume: int = 1_000_000,
) -> MagicMock:
    """Create a fake MarketData-like object."""
    row = MagicMock()
    row.date = d
    row.open = Decimal(str(open_))
    row.high = Decimal(str(high))
    row.low = Decimal(str(low))
    row.close = Decimal(str(close))
    row.volume = volume
    return row


def make_rows(n: int = 5, gap: int = 1) -> list[MagicMock]:
    """Create *n* consecutive rows, each *gap* days apart."""
    base = date(2026, 1, 2)
    return [make_row(base + timedelta(days=i * gap)) for i in range(n)]


def make_session_factory(ticker_symbol: str, rows: list, *, ticker_id=None):
    """
    Return an async_sessionmaker-like callable whose sessions first yield a
    Ticker result (for the symbol lookup) and then a MarketData result.
    """
    if ticker_id is None:
        ticker_id = uuid.uuid4()

    fake_ticker = MagicMock()
    fake_ticker.id = ticker_id
    fake_ticker.symbol = ticker_symbol

    ticker_result = MagicMock()
    ticker_result.scalar_one_or_none.return_value = fake_ticker

    md_result = MagicMock()
    md_result.scalars.return_value.all.return_value = rows

    session = AsyncMock()
    # First call → ticker lookup; second call → market data
    session.execute.side_effect = [ticker_result, md_result]

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock()
    factory.return_value = cm
    # Allow "async with factory() as session" pattern
    factory.side_effect = lambda: cm
    return factory


def make_all_session_factory(symbols: list[str], rows_per_symbol: int = 5):
    """
    Return a session factory that handles:
    1. get_all_symbols() query → returns list of symbol strings
    2. For each symbol: Ticker lookup + MarketData lookup
    """
    # Result for get_all_symbols
    symbol_result = MagicMock()
    symbol_result.all.return_value = [(s,) for s in symbols]

    calls = [0]

    async def _execute(stmt):
        calls[0] += 1
        # First call is get_all_symbols
        if calls[0] == 1:
            return symbol_result
        # Subsequent calls alternate Ticker / MarketData
        pair_index = (calls[0] - 2) % 2
        if pair_index == 0:
            # Ticker lookup
            idx = (calls[0] - 2) // 2
            ticker_obj = MagicMock()
            ticker_obj.id = uuid.uuid4()
            ticker_obj.symbol = symbols[idx] if idx < len(symbols) else symbols[0]
            r = MagicMock()
            r.scalar_one_or_none.return_value = ticker_obj
            return r
        else:
            # MarketData lookup
            rows = make_rows(rows_per_symbol)
            r = MagicMock()
            r.scalars.return_value.all.return_value = rows
            return r

    session = AsyncMock()
    session.execute.side_effect = _execute

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    factory = MagicMock()
    factory.side_effect = lambda: cm
    return factory


# ---------------------------------------------------------------------------
# Rule function unit tests
# ---------------------------------------------------------------------------


class TestRulePositivePrices:
    def test_pass_all_positive(self):
        rows = [make_row(date(2026, 1, 2))]
        assert _check_positive_prices("AAPL", rows) == []

    def test_fail_zero_close(self):
        rows = [make_row(date(2026, 1, 2), close=0.0)]
        msgs = _check_positive_prices("AAPL", rows)
        assert len(msgs) == 1
        assert "close" in msgs[0]

    def test_fail_negative_open(self):
        rows = [make_row(date(2026, 1, 2), open_=-5.0)]
        msgs = _check_positive_prices("AAPL", rows)
        assert any("open" in m for m in msgs)

    def test_multiple_issues(self):
        rows = [make_row(date(2026, 1, 2), open_=-1, close=0.0)]
        msgs = _check_positive_prices("AAPL", rows)
        assert len(msgs) == 2


class TestRuleNoLargeGaps:
    def test_pass_consecutive_days(self):
        rows = make_rows(5, gap=1)
        assert _check_no_large_gaps("AAPL", rows) == []

    def test_fail_gap_of_8(self):
        rows = [make_row(date(2026, 1, 2)), make_row(date(2026, 1, 10))]
        msgs = _check_no_large_gaps("AAPL", rows)
        assert len(msgs) == 1
        assert "8 days" in msgs[0]

    def test_pass_weekend_gap_of_3(self):
        # Friday to Monday is 3 days, within the 5-day threshold
        rows = [make_row(date(2026, 1, 2)), make_row(date(2026, 1, 5))]
        assert _check_no_large_gaps("AAPL", rows) == []


class TestRuleDailyChangeLt50:
    def test_pass_normal_change(self):
        rows = [
            make_row(date(2026, 1, 2), close=100.0),
            make_row(date(2026, 1, 3), close=110.0),  # +10%
        ]
        assert _check_daily_change_lt50("AAPL", rows) == []

    def test_fail_large_spike(self):
        rows = [
            make_row(date(2026, 1, 2), close=100.0),
            make_row(date(2026, 1, 3), close=200.0),  # +100%
        ]
        msgs = _check_daily_change_lt50("AAPL", rows)
        assert len(msgs) == 1
        assert "100.0%" in msgs[0]

    def test_fail_large_drop(self):
        rows = [
            make_row(date(2026, 1, 2), close=100.0),
            make_row(date(2026, 1, 3), close=40.0),  # -60%
        ]
        msgs = _check_daily_change_lt50("AAPL", rows)
        assert len(msgs) == 1


class TestRulePositiveVolume:
    def test_pass_positive_volume(self):
        rows = [make_row(date(2026, 1, 2), volume=500_000)]
        assert _check_positive_volume("AAPL", rows) == []

    def test_fail_zero_volume(self):
        rows = [make_row(date(2026, 1, 2), volume=0)]
        msgs = _check_positive_volume("AAPL", rows)
        assert len(msgs) == 1
        assert "volume=0" in msgs[0]

    def test_fail_negative_volume(self):
        rows = [make_row(date(2026, 1, 2), volume=-100)]
        msgs = _check_positive_volume("AAPL", rows)
        assert len(msgs) == 1


# ---------------------------------------------------------------------------
# QualityIssue dataclass
# ---------------------------------------------------------------------------


def test_quality_issue_str():
    issue = QualityIssue(
        ticker="AAPL",
        rule_name="positive_prices",
        severity="critical",
        message="close=0 on 2026-01-02",
    )
    s = str(issue)
    assert "[CRITICAL]" in s
    assert "AAPL" in s
    assert "positive_prices" in s


def test_quality_issue_detected_at_auto():
    before = datetime.utcnow()
    issue = QualityIssue(ticker="X", rule_name="r", severity="warning", message="m")
    after = datetime.utcnow()
    assert before <= issue.detected_at <= after


# ---------------------------------------------------------------------------
# DataQualityMonitor — run_checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_checks_empty_data_returns_empty():
    """When DB has no rows for the ticker, return empty list."""
    # Ticker not found → empty rows
    ticker_result = MagicMock()
    ticker_result.scalar_one_or_none.return_value = None

    session = AsyncMock()
    session.execute.return_value = ticker_result

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(side_effect=lambda: cm)

    monitor = DataQualityMonitor(session_factory=mock_factory)
    issues = await monitor.run_checks("AAPL")
    assert issues == []


@pytest.mark.asyncio
async def test_run_checks_healthy_data():
    """Clean data → no quality issues."""
    rows = make_rows(10, gap=1)
    factory = make_session_factory("AAPL", rows)
    monitor = DataQualityMonitor(session_factory=factory)
    issues = await monitor.run_checks("AAPL")
    assert issues == []


@pytest.mark.asyncio
async def test_run_checks_detects_bad_data():
    """Bad data → at least one critical issue from positive_prices rule."""
    rows = [make_row(date(2026, 1, 2), close=0.0)]  # close = 0 → critical
    factory = make_session_factory("AAPL", rows)
    monitor = DataQualityMonitor(session_factory=factory)
    issues = await monitor.run_checks("AAPL")
    assert any(i.severity == "critical" for i in issues)
    assert any(i.rule_name == "positive_prices" for i in issues)


@pytest.mark.asyncio
async def test_run_checks_detects_gap():
    """Data gap of 10 days → no_large_gaps warning."""
    rows = [make_row(date(2026, 1, 2)), make_row(date(2026, 1, 12))]
    factory = make_session_factory("AAPL", rows)
    monitor = DataQualityMonitor(session_factory=factory)
    issues = await monitor.run_checks("AAPL")
    assert any(i.rule_name == "no_large_gaps" for i in issues)
    assert all(i.severity == "warning" for i in issues if i.rule_name == "no_large_gaps")


# ---------------------------------------------------------------------------
# DataQualityMonitor — run_all_checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_all_checks_no_tickers():
    """When the DB has no tickers, return empty dict."""
    symbol_result = MagicMock()
    symbol_result.all.return_value = []

    session = AsyncMock()
    session.execute.return_value = symbol_result

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(side_effect=lambda: cm)

    monitor = DataQualityMonitor(session_factory=mock_factory)
    report = await monitor.run_all_checks()
    assert report == {}


@pytest.mark.asyncio
async def test_run_all_checks_with_multiple_tickers():
    """run_all_checks builds a report dict with one entry per symbol."""
    symbols = ["AAPL", "MSFT", "NVDA"]

    # We patch run_checks to avoid complex session mocking for all symbols
    async def fake_run_checks(self_or_ticker, ticker=None):
        # Called as instance method → first arg is self, rest is ticker
        if ticker is None:
            ticker = self_or_ticker
        return []

    with patch.object(DataQualityMonitor, "run_checks", new=AsyncMock(return_value=[])):
        # Patch _get_all_symbols to return our list
        with patch.object(
            DataQualityMonitor, "_get_all_symbols", new=AsyncMock(return_value=symbols)
        ):
            monitor = DataQualityMonitor(session_factory=MagicMock())
            report = await monitor.run_all_checks()

    assert set(report.keys()) == set(symbols)
    for v in report.values():
        assert v == []


@pytest.mark.asyncio
async def test_run_all_checks_includes_issues():
    """When run_checks returns issues, they are reflected in the report."""
    fake_issue = QualityIssue(
        ticker="AAPL",
        rule_name="positive_prices",
        severity="critical",
        message="close=0 on 2026-01-02",
    )
    with patch.object(
        DataQualityMonitor, "_get_all_symbols", new=AsyncMock(return_value=["AAPL"])
    ):
        with patch.object(
            DataQualityMonitor, "run_checks", new=AsyncMock(return_value=[fake_issue])
        ):
            monitor = DataQualityMonitor(session_factory=MagicMock())
            report = await monitor.run_all_checks()

    assert len(report["AAPL"]) == 1
    assert report["AAPL"][0].rule_name == "positive_prices"


# ---------------------------------------------------------------------------
# Scheduler job
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_daily_quality_check_job():
    """daily_quality_check job calls run_all_checks without raising."""
    from src.infra.scheduler.jobs import daily_quality_check

    mock_report = {"AAPL": [], "MSFT": []}

    with patch(
        "src.market_data.services.quality_monitor.DataQualityMonitor",
    ) as MockMonitor:
        instance = AsyncMock()
        instance.run_all_checks = AsyncMock(return_value=mock_report)
        MockMonitor.return_value = instance

        await daily_quality_check()

    instance.run_all_checks.assert_awaited_once()


# ---------------------------------------------------------------------------
# Default rules completeness
# ---------------------------------------------------------------------------


def test_default_rules_count():
    assert len(DEFAULT_RULES) == 4


def test_default_rules_names():
    names = {r.name for r in DEFAULT_RULES}
    assert "positive_prices" in names
    assert "no_large_gaps" in names
    assert "daily_change_lt50" in names
    assert "positive_volume" in names


def test_default_rules_has_critical():
    severities = {r.severity for r in DEFAULT_RULES}
    assert "critical" in severities
    assert "warning" in severities
