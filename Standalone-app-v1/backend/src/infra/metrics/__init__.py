"""Prometheus metrics package — Tasks 3.6 / 3.10."""

from src.infra.metrics.metrics import (
    active_estimates_total,
    # Technical metrics
    api_request_duration_seconds,
    cache_hits_total,
    cache_misses_total,
    current_portfolio_pnl,
    db_pool_checked_in,
    # Pool metrics (Task 3.10)
    db_pool_checked_out,
    db_pool_overflow,
    db_pool_size,
    drive_sync_operations_total,
    estimates_closed_total,
    # Business metrics
    estimates_created_total,
    # Decorator
    track_duration,
    update_pool_metrics,
    yahoo_api_calls_total,
)
from src.infra.metrics.routes import router

__all__ = [
    # Business
    "estimates_created_total",
    "estimates_closed_total",
    "active_estimates_total",
    "current_portfolio_pnl",
    # Technical
    "api_request_duration_seconds",
    "yahoo_api_calls_total",
    "drive_sync_operations_total",
    "cache_hits_total",
    "cache_misses_total",
    # Pool (Task 3.10)
    "db_pool_checked_out",
    "db_pool_checked_in",
    "db_pool_overflow",
    "db_pool_size",
    "update_pool_metrics",
    # Decorator
    "track_duration",
    # Router
    "router",
]
