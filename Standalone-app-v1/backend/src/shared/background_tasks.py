import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.shared.infra.config import get_settings
from src.shared.infra.database import AsyncSessionLocal
from src.shared.domain.app_config import AppConfig
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.shared.services.sse_manager import sse_manager
from src.market_data.finnhub_client import get_quote
from src.market_data.yahoo_client import get_current_price

logger = logging.getLogger(__name__)

_RUNTIME_STATUS: dict[str, Any] = {
    "running": False,
    "next_run_iso": None,
    "last_run_iso": None,
    "estimates_monitored": 0,
    "last_yahoo_call": None,
}


def _isoformat_utc(value: datetime) -> str:
    return value.isoformat()


def _set_last_yahoo_call(timestamp: datetime, success: bool) -> None:
    _RUNTIME_STATUS["last_yahoo_call"] = {
        "timestamp": _isoformat_utc(timestamp),
        "success": success,
    }


def get_price_loop_runtime_status() -> dict[str, Any]:
    last_yahoo_call = _RUNTIME_STATUS.get("last_yahoo_call")

    return {
        "running": _RUNTIME_STATUS.get("running", False),
        "next_run_iso": _RUNTIME_STATUS.get("next_run_iso"),
        "last_run_iso": _RUNTIME_STATUS.get("last_run_iso"),
        "estimates_monitored": _RUNTIME_STATUS.get("estimates_monitored", 0),
        "last_yahoo_call": dict(last_yahoo_call) if isinstance(last_yahoo_call, dict) else None,
    }


async def _resolve_price_loop_interval_seconds(default_seconds: int) -> int:
    try:
        async with AsyncSessionLocal() as db_session:
            result = await db_session.execute(
                select(AppConfig).where(AppConfig.key == "GLOBAL_CONFIG")
            )
            config = result.scalar_one_or_none()
            if not config:
                return default_seconds

            data = json.loads(config.value)
            minutes_value = data.get("price_update_interval_minutes")
            if minutes_value is None:
                return default_seconds

            minutes = int(minutes_value)
            return minutes * 60 if minutes > 0 else default_seconds
    except Exception as exc:
        logger.warning(
            "Unable to resolve GLOBAL_CONFIG interval, using fallback",
            exc_info=exc,
        )
        return default_seconds

async def start_price_loop(context: dict = None):
    """
    Continuous background loop that fetches active symbols from DB, 
    refreshes live prices ticker by ticker (using Yahoo v8 with Finnhub fallback),
    evaluates take-profit/stop-loss, closes estimates if targets are reached, 
    and broadcasts updates via SSE.
    Continues on single ticker error.
    """
    settings = get_settings()
    default_interval_seconds = int(getattr(settings, "PRICE_LOOP_INTERVAL_SECONDS", 60))
    interval_seconds = await _resolve_price_loop_interval_seconds(default_interval_seconds)
    _RUNTIME_STATUS["running"] = True
    _RUNTIME_STATUS["next_run_iso"] = _isoformat_utc(
        datetime.now(timezone.utc) + timedelta(seconds=interval_seconds)
    )
    
    logger.info(f"Starting background price loop, interval={interval_seconds}s...")
    
    while True:
        try:
            loop_started_at = datetime.now(timezone.utc)
            _RUNTIME_STATUS["last_run_iso"] = _isoformat_utc(loop_started_at)
            _RUNTIME_STATUS["next_run_iso"] = _isoformat_utc(
                loop_started_at + timedelta(seconds=interval_seconds)
            )

            active_estimates = []
            async with AsyncSessionLocal() as db_session:
                stmt = (
                    select(Estimate)
                    .where(Estimate.status == EstimateStatus.OPEN)
                    .where(Estimate.is_deleted == False)
                    .options(selectinload(Estimate.ticker))
                )
                result = await db_session.execute(stmt)
                active_estimates = result.scalars().all()
            
            checked_count = len(active_estimates)
            _RUNTIME_STATUS["estimates_monitored"] = checked_count
            closed_count = 0

            if active_estimates:
                estimates_by_symbol = {}
                for est in active_estimates:
                    if est.ticker and est.ticker.symbol:
                        estimates_by_symbol.setdefault(est.ticker.symbol, []).append(est)

                for symbol, estimates in estimates_by_symbol.items():
                    try:
                        yahoo_attempt_at = datetime.now(timezone.utc)
                        curr_price = await get_current_price(symbol)
                        _set_last_yahoo_call(yahoo_attempt_at, curr_price is not None)
                        
                        if curr_price is None:
                            quote_data = await get_quote(symbol)
                            if quote_data and quote_data.get("c") is not None:
                                curr_price = float(quote_data["c"])

                        if curr_price is not None:
                            async with AsyncSessionLocal() as inner_session:
                                changes_made = False
                                for est in estimates:
                                    est_in_inner = await inner_session.get(Estimate, est.id)
                                    if not est_in_inner or est_in_inner.status != EstimateStatus.OPEN:
                                        continue

                                    closed_state = None
                                    trigger_val = None
                                    
                                    if est_in_inner.target_price and curr_price >= float(est_in_inner.target_price):
                                        closed_state = EstimateStatus.CLOSED_WIN
                                        trigger_val = float(est_in_inner.target_price)
                                    elif est_in_inner.stop_loss_price and curr_price <= float(est_in_inner.stop_loss_price):
                                        closed_state = EstimateStatus.CLOSED_LOSS
                                        trigger_val = float(est_in_inner.stop_loss_price)

                                    if closed_state:
                                        est_in_inner.status = closed_state
                                        est_in_inner.exit_price = trigger_val
                                        est_in_inner.closed_at = datetime.now(timezone.utc)
                                        # NOTE: realized_pnl è delta prezzo unitario, non P&L totale
                                        est_in_inner.realized_pnl = float(trigger_val) - float(est_in_inner.start_price)
                                        changes_made = True
                                        closed_count += 1
                                        
                                        logger.info(f"Estimate {est_in_inner.id} closed as {closed_state.value} at trigger {trigger_val}.")

                                        await sse_manager.broadcast({
                                            "type": "estimate_update",
                                            "estimate_id": str(est_in_inner.id),
                                            "new_state": closed_state.value,
                                            "trigger_price": float(trigger_val)
                                        })
                                
                                if changes_made:
                                    await inner_session.commit()

                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        _set_last_yahoo_call(datetime.now(timezone.utc), False)
                        logger.error(f"Errore aggiornamento prezzo per il ticker {symbol}: {e}")
                        continue

            logger.info(f"Price loop tick: {checked_count} estimates checked, {closed_count} closed.")

        except asyncio.CancelledError:
            _RUNTIME_STATUS["running"] = False
            logger.info("Price loop fermato.")
            return
        except Exception as e:
            logger.error(f"Error in overall price loop: {e}", exc_info=True)
            
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            _RUNTIME_STATUS["running"] = False
            logger.info("Price loop fermato.")
            return
