import asyncio
import logging
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.domain.entities import Ticker
from src.market_data.services.yahoo_service import YahooFinanceService
from src.shared.services.sse_manager import sse_manager
from src.shared.infra.config import get_settings

logger = logging.getLogger(__name__)

async def start_price_loop(app_state: dict):
    """
    Continuous background loop that fetches active symbols from DB, 
    refreshes live prices ticker by ticker, and broadcasts updates via SSE.
    Continues on single ticker error.
    """
    settings = get_settings()
    logger.info(f"Starting background price loop, interval={settings.PRICE_UPDATE_INTERVAL_MINUTES}m...")
    
    while True:
        try:
            db_session_factory = app_state.get('db_session')
            if not db_session_factory:
                logger.error("No db_session_factory provided in app_state")
                await asyncio.sleep(60)
                continue

            active_estimates = []
            async with db_session_factory() as db_session:
                # 1. Fetch OPEN estimates with their Ticker
                stmt = (
                    select(Estimate)
                    .where(Estimate.status == EstimateStatus.OPEN)
                    .where(Estimate.is_deleted == False)
                    .options(selectinload(Estimate.ticker))
                )
                result = await db_session.execute(stmt)
                active_estimates = result.scalars().all()
            
            if active_estimates:
                # Group estimates by ticker symbol to minimize Yahoo API calls
                estimates_by_symbol = {}
                for est in active_estimates:
                    if est.ticker and est.ticker.symbol:
                        estimates_by_symbol.setdefault(est.ticker.symbol, []).append(est)

                # 2. Fetch prices ticker by ticker, log single errors, continue
                for symbol, estimates in estimates_by_symbol.items():
                    try:
                        # Assuming YahooFinanceService can fetch for a list
                        # MOCK: for demonstration we use YahooFinanceService.get_live_prices
                        # In real scenario we should await a true Yahoo fetcher
                        ticker_prices = await YahooFinanceService.get_live_prices([symbol])
                        current_price = ticker_prices.get(symbol)
                        
                        if current_price is not None:
                            # 3. Push to SSE Broadcaster for each estimate
                            for est in estimates:
                                await sse_manager.broadcast({
                                    "type": "estimate_update",
                                    "estimate_id": str(est.id),
                                    "new_state": "OPEN",  # Basic logic, can be evaluated
                                    "trigger_price": float(current_price)
                                })
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        # Log error for the single ticker and CONTINUE with the next one
                        logger.error(f"Errore aggiornamento prezzo per il ticker {symbol}: {e}")
                        continue

        except asyncio.CancelledError:
            logger.info("Price loop cancelled, shutting down.")
            break
        except Exception as e:
            logger.error(f"Error in overall price loop: {e}", exc_info=True)
            
        await asyncio.sleep(settings.PRICE_UPDATE_INTERVAL_MINUTES * 60)
