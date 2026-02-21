"""
Data Quality Monitor — TASK 3.8

Monitors data quality for all tracked market-data tickers.

Architecture
------------
- ``QualityRule``  : named, callable rule with a severity level.
- ``QualityIssue`` : a single failed-rule event for one ticker on one date.
- ``DataQualityMonitor`` : service that loads market data from the DB and
  applies all registered rules in parallel, one ticker at a time.

Default rules
-------------
1. positive_prices   (critical) — open/high/low/close must all be > 0
2. no_large_gaps     (warning)  — no gap > 5 calendar days between consecutive rows
3. daily_change_lt50 (warning)  — daily close change ≤ ±50 %
4. positive_volume   (warning)  — volume must be > 0

Severity semantics
------------------
- ``critical`` → logged as ERROR + alert emitted to structlog
- ``warning``  → logged as WARNING
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Callable, Dict, List, Literal, Optional

from sqlalchemy import select

import structlog

from src.market_data.domain.entities import Ticker
from src.market_data.domain.market_data import MarketData
from src.shared.infra.database import AsyncSessionLocal

Severity = Literal["warning", "critical"]

_logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class QualityRule:
    """
    A single data-quality rule that can be applied to market data rows.

    Attributes:
        name:        Short unique identifier (used as ``rule_name`` in issues).
        description: Human-readable explanation of what the rule checks.
        check_fn:    Callable ``(ticker: str, rows: List[MarketData]) → List[str]``
                     that returns a list of issue message strings (empty = pass).
        severity:    "warning" | "critical"
    """

    name: str
    description: str
    check_fn: Callable[[str, List[MarketData]], List[str]]
    severity: Severity


@dataclass
class QualityIssue:
    """
    A single data-quality problem detected for one ticker.

    Attributes:
        ticker:      Trading symbol (e.g., "AAPL").
        rule_name:   Name of the ``QualityRule`` that produced this issue.
        severity:    Inherited from the rule.
        message:     Human-readable description of the specific problem.
        detected_at: UTC timestamp of detection (auto-set on creation).
    """

    ticker: str
    rule_name: str
    severity: Severity
    message: str
    detected_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        return (
            f"[{self.severity.upper()}] {self.ticker} / {self.rule_name}: {self.message}"
        )


# ---------------------------------------------------------------------------
# Built-in rule check functions
# ---------------------------------------------------------------------------


def _check_positive_prices(ticker: str, rows: List[MarketData]) -> List[str]:
    """Rule: all OHLC prices must be strictly positive."""
    issues: List[str] = []
    for row in rows:
        for field_name, value in [
            ("open", row.open),
            ("high", row.high),
            ("low", row.low),
            ("close", row.close),
        ]:
            if value is not None and Decimal(str(value)) <= 0:
                issues.append(
                    f"{row.date}: {field_name}={value} is not positive"
                )
    return issues


def _check_no_large_gaps(ticker: str, rows: List[MarketData]) -> List[str]:
    """Rule: no gap > 5 calendar days between consecutive data rows."""
    issues: List[str] = []
    sorted_rows = sorted(rows, key=lambda r: r.date)
    for prev, curr in zip(sorted_rows, sorted_rows[1:]):
        delta = (curr.date - prev.date).days
        if delta > 5:
            issues.append(
                f"Gap of {delta} days between {prev.date} and {curr.date}"
            )
    return issues


def _check_daily_change_lt50(ticker: str, rows: List[MarketData]) -> List[str]:
    """Rule: daily close-to-close change must be ≤ ±50 %."""
    issues: List[str] = []
    sorted_rows = sorted(rows, key=lambda r: r.date)
    for prev, curr in zip(sorted_rows, sorted_rows[1:]):
        if prev.close and Decimal(str(prev.close)) != 0:
            pct = abs(
                (Decimal(str(curr.close)) - Decimal(str(prev.close)))
                / Decimal(str(prev.close))
            )
            if pct > Decimal("0.50"):
                issues.append(
                    f"{curr.date}: close changed {float(pct)*100:.1f}% vs {prev.date}"
                )
    return issues


def _check_positive_volume(ticker: str, rows: List[MarketData]) -> List[str]:
    """Rule: trading volume must be > 0."""
    issues: List[str] = []
    for row in rows:
        if row.volume is not None and int(row.volume) <= 0:
            issues.append(f"{row.date}: volume={row.volume} is not positive")
    return issues


# ---------------------------------------------------------------------------
# Default rule set
# ---------------------------------------------------------------------------

DEFAULT_RULES: List[QualityRule] = [
    QualityRule(
        name="positive_prices",
        description="All OHLC prices must be strictly positive (> 0)",
        check_fn=_check_positive_prices,
        severity="critical",
    ),
    QualityRule(
        name="no_large_gaps",
        description="No gap > 5 calendar days between consecutive data rows",
        check_fn=_check_no_large_gaps,
        severity="warning",
    ),
    QualityRule(
        name="daily_change_lt50",
        description="Daily close-to-close change must be ≤ ±50 %",
        check_fn=_check_daily_change_lt50,
        severity="warning",
    ),
    QualityRule(
        name="positive_volume",
        description="Trading volume must be > 0",
        check_fn=_check_positive_volume,
        severity="warning",
    ),
]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class DataQualityMonitor:
    """
    Runs data-quality checks for market data tickers.

    Usage
    -----
    .. code-block:: python

        monitor = DataQualityMonitor()
        issues = await monitor.run_checks("AAPL")
        report = await monitor.run_all_checks()

    Constructor parameters
    ----------------------
    rules:
        List of QualityRule objects to apply. Defaults to ``DEFAULT_RULES``.
    lookback_days:
        Number of calendar days of history to load per ticker (default: 60).
    session_factory:
        Optional async_sessionmaker; if None the module-level
        ``AsyncSessionLocal`` is used (suitable for production).
    """

    def __init__(
        self,
        rules: Optional[List[QualityRule]] = None,
        lookback_days: int = 60,
        session_factory=None,
    ) -> None:
        self._rules: List[QualityRule] = rules if rules is not None else list(DEFAULT_RULES)
        self._lookback_days = lookback_days
        self._session_factory = session_factory or AsyncSessionLocal

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_ticker_rows(
        self, ticker_symbol: str, start: date
    ) -> List[MarketData]:
        """Load MarketData rows for *ticker_symbol* from *start* to today."""
        async with self._session_factory() as session:
            # Look up the Ticker to get its UUID
            ticker_result = await session.execute(
                select(Ticker).where(Ticker.symbol == ticker_symbol)
            )
            ticker: Optional[Ticker] = ticker_result.scalar_one_or_none()
            if ticker is None:
                return []

            # Fetch history
            md_result = await session.execute(
                select(MarketData)
                .where(
                    MarketData.ticker_id == ticker.id,
                    MarketData.date >= start,
                )
                .order_by(MarketData.date.asc())
            )
            return list(md_result.scalars().all())

    async def _get_all_symbols(self) -> List[str]:
        """Return all ticker symbols stored in the database."""
        async with self._session_factory() as session:
            result = await session.execute(select(Ticker.symbol))
            return [row[0] for row in result.all()]

    def _apply_rules(
        self, ticker: str, rows: List[MarketData]
    ) -> List[QualityIssue]:
        """Apply all rules to the provided rows; return list of issues."""
        issues: List[QualityIssue] = []
        for rule in self._rules:
            try:
                messages = rule.check_fn(ticker, rows)
                for msg in messages:
                    issues.append(
                        QualityIssue(
                            ticker=ticker,
                            rule_name=rule.name,
                            severity=rule.severity,
                            message=msg,
                        )
                    )
            except Exception as exc:
                _logger.error(
                    "quality_rule_error",
                    ticker=ticker,
                    rule=rule.name,
                    error=str(exc),
                )
        return issues

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_checks(self, ticker: str) -> List[QualityIssue]:
        """
        Run all quality rules for a single ticker.

        Args:
            ticker: Trading symbol (e.g., "AAPL").

        Returns:
            List of QualityIssue objects (empty list = everything OK).
        """
        start = date.today() - timedelta(days=self._lookback_days)
        rows = await self._get_ticker_rows(ticker, start)

        if not rows:
            _logger.warning(
                "quality_monitor_no_data",
                ticker=ticker,
                lookback_days=self._lookback_days,
            )
            return []

        issues = self._apply_rules(ticker, rows)
        self._log_issues(ticker, issues)
        return issues

    async def run_all_checks(self) -> Dict[str, List[QualityIssue]]:
        """
        Run quality checks for every ticker in the database (parallel).

        Returns:
            Dict mapping ticker symbol → list of QualityIssue.
            Tickers with no issues are **included** with an empty list.
        """
        symbols = await self._get_all_symbols()
        if not symbols:
            _logger.warning("quality_monitor_no_tickers")
            return {}

        tasks = [self.run_checks(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        report: Dict[str, List[QualityIssue]] = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                _logger.error(
                    "quality_monitor_ticker_error",
                    ticker=symbol,
                    error=str(result),
                )
                report[symbol] = []
            else:
                report[symbol] = result  # type: ignore[assignment]

        self._log_summary(report)
        return report

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _log_issues(self, ticker: str, issues: List[QualityIssue]) -> None:
        """Log individual issues; emit ERROR for critical ones (alert)."""
        for issue in issues:
            if issue.severity == "critical":
                _logger.error(
                    "quality_issue_critical",
                    ticker=ticker,
                    rule=issue.rule_name,
                    message=issue.message,
                    detected_at=issue.detected_at.isoformat(),
                    alert=True,
                )
            else:
                _logger.warning(
                    "quality_issue_warning",
                    ticker=ticker,
                    rule=issue.rule_name,
                    message=issue.message,
                    detected_at=issue.detected_at.isoformat(),
                )

    def _log_summary(self, report: Dict[str, List[QualityIssue]]) -> None:
        """Log a daily summary of the quality check run."""
        total_tickers = len(report)
        tickers_with_issues = sum(1 for v in report.values() if v)
        critical_count = sum(
            1 for issues in report.values()
            for issue in issues
            if issue.severity == "critical"
        )
        warning_count = sum(
            1 for issues in report.values()
            for issue in issues
            if issue.severity == "warning"
        )
        _logger.info(
            "quality_monitor_daily_report",
            total_tickers=total_tickers,
            tickers_with_issues=tickers_with_issues,
            critical_issues=critical_count,
            warning_issues=warning_count,
        )
        if critical_count > 0:
            _logger.error(
                "quality_monitor_alert",
                critical_issues=critical_count,
                detail=[
                    str(issue)
                    for issues in report.values()
                    for issue in issues
                    if issue.severity == "critical"
                ],
            )
