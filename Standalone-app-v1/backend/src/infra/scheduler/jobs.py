"""
Scheduler job implementations for background processing.

This module contains the actual job functions that are executed by APScheduler.
Jobs include:
- Outbox event processing
- Dead letter handling
- Market data refresh
- Daily history sync
- Materialized view refresh
- Target/stop checking
"""

import logging
from datetime import UTC

from sqlalchemy.ext.asyncio import async_sessionmaker

from src.infra.outbox.outbox_processor import OutboxProcessor

logger = logging.getLogger("scheduler.jobs")

# Global references for dependency injection
_session_factory: async_sessionmaker | None = None
_sync_service: object | None = None


def configure_jobs(session_factory: async_sessionmaker, sync_service: object | None = None):
    """
    Configure jobs with dependencies.

    Must be called before scheduler starts to inject dependencies.

    Args:
        session_factory: SQLAlchemy async session factory
        sync_service: SyncService instance (optional)
    """
    global _session_factory, _sync_service
    _session_factory = session_factory
    _sync_service = sync_service
    logger.info("Scheduler jobs configured with dependencies")


async def process_outbox_events():
    """
    Process unprocessed outbox events with Drive sync.

    Runs every 30 seconds to ensure timely event processing.
    Handles:
    - Fetching unprocessed events
    - Syncing to Drive
    - Updating event status
    - Retry logic
    """
    if _session_factory is None:
        logger.error("Scheduler jobs not configured - skipping outbox processing")
        return

    try:
        processor = OutboxProcessor(_session_factory, _sync_service)
        result = await processor.process_pending_events()

        logger.info(
            "Outbox processing completed",
            extra={
                "job": "process_outbox_events",
                "processed": result["processed"],
                "failed": result["failed"],
                "skipped": result["skipped"],
            }
        )

    except Exception as e:
        logger.exception(f"Error in process_outbox_events job: {e}")


async def handle_dead_letters():
    """
    Handle dead letter events (max retries exceeded).

    Runs daily at 02:00 UTC to identify and log events that
    require manual intervention.
    """
    if _session_factory is None:
        logger.error("Scheduler jobs not configured - skipping dead letter handling")
        return

    try:
        processor = OutboxProcessor(_session_factory, _sync_service)
        count = await processor.handle_dead_letters()

        logger.info(
            "Dead letter handling completed",
            extra={
                "job": "handle_dead_letters",
                "dead_letter_count": count,
            }
        )

        if count > 0:
            logger.warning(
                f"Found {count} dead letter events requiring manual intervention"
            )

    except Exception as e:
        logger.exception(f"Error in handle_dead_letters job: {e}")


# Placeholder job implementations (to be implemented in future tasks)

async def refresh_market_data():
    """
    Fetch and update current market data for active tickers.

    Runs every 5 minutes during market hours (14:00-21:00 UTC, Mon-Fri).
    """
    logger.debug("refresh_market_data job executed (placeholder)")
    # TODO: Implement market data refresh logic


async def daily_history_sync():
    """
    Sync daily historical data for all active tickers.

    Runs daily at 23:00 UTC after market close.
    """
    if _session_factory is None:
        logger.error("Scheduler jobs not configured - skipping daily_history_sync")
        return

    logger.debug("daily_history_sync job executed")
    try:
        from datetime import datetime, timedelta

        from sqlalchemy import select

        from src.estimates.domain.entities import Estimate, EstimateStatus
        from src.market_data.repositories.market_data_repository import MarketDataRepository
        from src.market_data.services.market_data_service import MarketDataService
        from src.market_data.services.yahoo_provider import YahooProvider

        async with _session_factory() as session:
            # Find distinct tickers from OPEN estimates
            stmt = select(Estimate.ticker_id).filter(Estimate.status == EstimateStatus.OPEN).distinct()
            result = await session.execute(stmt)
            active_ticker_ids = result.scalars().all()

            if not active_ticker_ids:
                logger.info("No active estimates found for history sync.")
                return

            provider = YahooProvider()
            repo = MarketDataRepository(_session_factory)
            service = MarketDataService(provider, repo, _session_factory)

            end_date = datetime.now(UTC).date()
            start_date = end_date - timedelta(days=60)  # Sync last 60 days

            for t_id in active_ticker_ids:
                try:
                    count = await service.sync_historical_data(t_id, start_date, end_date, interval="1d")
                    logger.info(f"Synced {count} days of OHLCV data for ticker {t_id}")
                except Exception as sync_err:
                    logger.error(f"Error syncing history for ticker {t_id}: {sync_err}")

    except Exception as e:
        logger.exception(f"Error in daily_history_sync job: {e}")


async def refresh_materialized_views():
    """
    Refresh materialized views for analytics.

    Runs every 5 minutes to keep analytics data fresh.
    """
    logger.debug("refresh_materialized_views job executed (placeholder)")
    # TODO: Implement materialized view refresh logic


async def check_targets():
    """
    Check if any estimates have hit target or stop prices.
    Uses conservative OHLCV checking (LONG only) via TargetEvaluationService.
    Runs every minute to ensure timely notifications.
    """
    if _session_factory is None:
        logger.error("Scheduler jobs not configured - skipping check_targets")
        return

    logger.debug("check_targets job executed")
    try:
        from datetime import datetime

        from sqlalchemy import select

        from src.estimates.domain.entities import Estimate, EstimateStatus
        from src.estimates.domain.services.target_checker import TargetEvaluationService
        from src.estimates.repositories.estimate_repository import EstimateRepository
        from src.market_data.repositories.market_data_repository import MarketDataRepository

        async with _session_factory() as session:
            stmt = select(Estimate).filter(Estimate.status == EstimateStatus.OPEN)
            result = await session.execute(stmt)
            open_estimates = result.scalars().all()

            if not open_estimates:
                return

            market_repo = MarketDataRepository(_session_factory)
            estimate_repo = EstimateRepository(_session_factory)

            for est in open_estimates:
                # get history from insertion to today
                today = datetime.now(UTC).date()
                history_data = await market_repo.get_history(
                    est.ticker_id,
                    est.created_at.date(),
                    today
                )

                if not history_data:
                    continue

                # Map MarketData to what TargetEvaluationService expects
                ohlcv_dicts = [
                    {
                        "date": m.date,
                        "open": m.open,
                        "high": m.high,
                        "low": m.low,
                        "close": m.close,
                        "volume": m.volume
                    } for m in history_data
                ]

                # Evaluate targets with conservative logic (e.g. 60 days duration)
                eval_result = TargetEvaluationService.evaluate_estimate(est, ohlcv_dicts, duration_days=60)

                if eval_result.hit:
                    # Update status
                    if eval_result.reason == "take_profit":
                        est.status = EstimateStatus.CLOSED_WIN
                    elif eval_result.reason == "stop_loss":
                        est.status = EstimateStatus.CLOSED_LOSS
                    else:
                        est.status = EstimateStatus.EXPIRED

                    est.closed_at = eval_result.exit_date
                    await session.merge(est) # Using session directly so we don't have to trigger complex logic if estimate_repo does not persist automatically.
                    await session.commit()
                    logger.info(f"Closed estimate {est.id} for ticker {est.ticker_id} with status {est.status}")

    except Exception as e:
        logger.exception(f"Error in check_targets job: {e}")


async def daily_quality_check():
    """
    Run data-quality checks for all market-data tickers.

    Instantiates DataQualityMonitor with default rules and calls
    run_all_checks(), which loads the last 60 days of OHLCV data per
    ticker and applies all registered QualityRules.

    Issues are logged automatically by the monitor:
    - WARNING for severity='warning' issues
    - ERROR  for severity='critical' issues (includes alert flag)

    Runs daily at 06:00 UTC (after European pre-market opens).
    """
    try:
        from src.market_data.services.quality_monitor import DataQualityMonitor

        monitor = DataQualityMonitor()
        report = await monitor.run_all_checks()

        total_issues = sum(len(v) for v in report.values())
        critical = sum(
            1
            for issues in report.values()
            for issue in issues
            if issue.severity == "critical"
        )
        logger.info(
            "[daily_quality_check] completed: %d tickers, %d issues (%d critical)",
            len(report),
            total_issues,
            critical,
        )
    except Exception as exc:
        logger.exception("[daily_quality_check] unexpected error: %s", exc)
