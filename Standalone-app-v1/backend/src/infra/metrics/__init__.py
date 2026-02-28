"""Prometheus metrics package — Tasks 3.6 / 3.10."""

from src.infra.metrics.metrics import (
    # Business metrics
    estimates_created_total,
    estimates_closed_total,
    active_estimates_total,
    current_portfolio_pnl,
    # Technical metrics
    api_request_duration_seconds,
    yahoo_api_calls_total,
    drive_sync_operations_total,
    cache_hits_total,
    cache_misses_total,
    # Pool metrics (Task 3.10)
    db_pool_checked_out,
    db_pool_checked_in,
    db_pool_overflow,
    db_pool_size,
    update_pool_metrics,
    # Decorator
    track_duration,
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
