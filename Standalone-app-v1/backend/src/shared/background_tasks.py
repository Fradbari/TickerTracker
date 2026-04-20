import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.shared.infra.config import get_settings
from src.shared.infra.database import AsyncSessionLocal
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.shared.services.sse_manager import sse_manager
from src.market_data.finnhub_client import get_quote
from src.market_data.yahoo_client import get_current_price

logger = logging.getLogger(__name__)

async def start_price_loop(context: dict = None):
    """
    Continuous background loop that fetches active symbols from DB, 
    refreshes live prices ticker by ticker (using Yahoo v8 with Finnhub fallback),
    evaluates take-profit/stop-loss, closes estimates if targets are reached, 
    and broadcasts updates via SSE.
    Continues on single ticker error.
    """
    settings = get_settings()
    interval_seconds = getattr(settings, "PRICE_LOOP_INTERVAL_SECONDS", 60)
    
    logger.info(f"Starting background price loop, interval={interval_seconds}s...")
    
    while True:
        try:
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
            closed_count = 0

            if active_estimates:
                estimates_by_symbol = {}
                for est in active_estimates:
                    if est.ticker and est.ticker.symbol:
                        estimates_by_symbol.setdefault(est.ticker.symbol, []).append(est)

                for symbol, estimates in estimates_by_symbol.items():
                    try:
                        curr_price = await get_current_price(symbol)
                        
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
                        logger.error(f"Errore aggiornamento prezzo per il ticker {symbol}: {e}")
                        continue

            logger.info(f"Price loop tick: {checked_count} estimates checked, {closed_count} closed.")

        except asyncio.CancelledError:
            logger.info("Price loop fermato.")
            return
        except Exception as e:
            logger.error(f"Error in overall price loop: {e}", exc_info=True)
            
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Price loop fermato.")
            return
