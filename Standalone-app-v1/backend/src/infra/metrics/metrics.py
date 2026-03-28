"""
Prometheus metrics definitions for TickerTracker backend (Task 3.6).

Exposes both *business* metrics (estimates lifecycle, portfolio P&L) and
*technical* metrics (API latency, external API call counts, cache efficiency).

All metrics use the default global ``REGISTRY`` so they are automatically
included in ``generate_latest()`` when the ``/metrics`` endpoint is called.

Usage
-----
Import individual metrics and update them in the relevant service/route::

    from src.infra.metrics.metrics import estimates_created_total
    estimates_created_total.labels(ticker="AAPL", ai_model="gpt-4o").inc()

Or use the ``@track_duration`` decorator for per-endpoint latency::

    from src.infra.metrics.metrics import track_duration, api_request_duration_seconds

    @router.get("/my-route")
    @track_duration(api_request_duration_seconds, endpoint="/my-route", method="GET")
    async def my_route():
        ...

Note on SecurityMiddleware overlap
-----------------------------------
SecurityMiddleware (Task 3.1) already logs ``duration_ms`` per request via
structlog.  ``@track_duration`` provides *finer-grained, per-endpoint*
latency in Prometheus histogram format.  Do NOT apply both to the same
endpoint for the same metric — choose one granularity level.
The concrete application of ``@track_duration`` to route handlers is the
responsibility of the task that introduces each route.
"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from typing import Any

from prometheus_client import Counter, Gauge, Histogram

# ---------------------------------------------------------------------------
# Business metrics
# ---------------------------------------------------------------------------

estimates_created_total = Counter(
    "estimates_created_total",
    "Total number of estimates created",
    labelnames=["ticker", "ai_model"],
)

estimates_closed_total = Counter(
    "estimates_closed_total",
    "Total number of estimates closed",
    labelnames=["ticker", "outcome"],
)

active_estimates_total = Gauge(
    "active_estimates_total",
    "Current number of active estimates by status",
    labelnames=["status"],
)

current_portfolio_pnl = Gauge(
    "current_portfolio_pnl",
    "Current portfolio P&L in base currency units",
)

# ---------------------------------------------------------------------------
# Technical metrics
# ---------------------------------------------------------------------------

# Latency histogram for API requests.
# Buckets cover the typical range from 5 ms to 30 s.
api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    labelnames=["endpoint", "method", "status"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0],
)

yahoo_api_calls_total = Counter(
    "yahoo_api_calls_total",
    "Total calls to the Yahoo Finance API",
    labelnames=["endpoint", "status"],
)

drive_sync_operations_total = Counter(
    "drive_sync_operations_total",
    "Total Google Drive sync operations",
    labelnames=["operation", "status"],
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    labelnames=["cache_name"],
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    labelnames=["cache_name"],
)

# ---------------------------------------------------------------------------
# Database connection pool metrics (Task 3.10)
# ---------------------------------------------------------------------------

db_pool_checked_out = Gauge(
    "db_pool_checked_out",
    "Number of connections currently checked out from the pool",
)

db_pool_checked_in = Gauge(
    "db_pool_checked_in",
    "Number of connections currently available in the pool",
)

db_pool_overflow = Gauge(
    "db_pool_overflow",
    "Number of overflow connections currently active",
)

db_pool_size = Gauge(
    "db_pool_size",
    "Configured pool size (max persistent connections)",
)


def update_pool_metrics() -> None:
    """
    Update Prometheus pool gauges from current engine state.

    Call this periodically (e.g. from the scheduler) or on-demand from the
    ``/metrics`` endpoint to keep gauges fresh.  Never raises — any error
    is silently swallowed so metrics collection cannot crash the application.
    """
    try:
        from src.shared.infra.database import get_pool_status

        status = get_pool_status()
        db_pool_checked_out.set(status["checked_out"])
        db_pool_checked_in.set(status["checked_in"])
        db_pool_overflow.set(status["overflow"])
        db_pool_size.set(status["pool_size"])
    except Exception:
        pass  # Never crash on metrics update


# ---------------------------------------------------------------------------
# @track_duration decorator
# ---------------------------------------------------------------------------


def track_duration(
    histogram: Histogram,
    **label_values: Any,
) -> Callable:
    """
    Decorator that records the wall-clock execution time of a route handler
    into a Prometheus ``Histogram``.

    Parameters
    ----------
    histogram:
        The :class:`prometheus_client.Histogram` to observe into.
    **label_values:
        Keyword arguments are forwarded verbatim to ``histogram.labels(...)``.
        Leave empty if the histogram has no labels.

    Examples
    --------
    Histogram with labels::

        @router.get("/estimates")
        @track_duration(
            api_request_duration_seconds,
            endpoint="/estimates",
            method="GET",
            status="200",
        )
        async def list_estimates():
            ...

    Histogram without labels::

        plain_hist = Histogram("plain_hist_seconds", "plain")

        @track_duration(plain_hist)
        def some_sync_fn():
            ...

    Notes
    -----
    - Works with both ``async def`` and ``def`` functions.
    - The timer starts immediately before the wrapped call and stops in a
      ``finally`` block so it is recorded even when an exception propagates.
    - Do NOT combine with ``SecurityMiddleware`` request logging for the same
      latency metric — choose one granularity level per endpoint.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                if label_values:
                    histogram.labels(**label_values).observe(elapsed)
                else:
                    histogram.observe(elapsed)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                if label_values:
                    histogram.labels(**label_values).observe(elapsed)
                else:
                    histogram.observe(elapsed)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
