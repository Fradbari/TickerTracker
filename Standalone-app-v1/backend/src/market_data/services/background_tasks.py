import asyncio
import logging
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.market_data.services.yahoo_service import YahooFinanceService
from src.shared.services.sse_manager import sse_manager

logger = logging.getLogger(__name__)

async def start_price_loop(app_state: dict):
    """
    Continuous background loop that fetches active symbols from DB, 
    refreshes live prices, and broadcasts updates via SSE.
    """
    logger.info("Starting background price loop...")
    while True:
        try:
            # 1. Fetch only ACTIVE estimates/symbols from DB
            db_session_factory = app_state.get('db_session')
            if db_session_factory:
                with db_session_factory() as db_session:
                    estimate_repo = EstimateRepository(db_session)
                    active_symbols = estimate_repo.get_active_symbols()
                    
                    if active_symbols:
                        # 2. Fetch prices (using yahoo proxy or backend service directly)
                        prices = await YahooFinanceService.get_live_prices(active_symbols)
                        
                        # 3. Push to SSE Broadcaster
                        await sse_manager.broadcast({
                            "event_type": "price_update",
                            "data": prices
                        })
        except asyncio.CancelledError:
            logger.info("Price loop cancelled, shutting down.")
            break
        except Exception as e:
            logger.error(f"Error in price loop: {e}", exc_info=True)
            
        # Standard interval between polling cycles = 15 seconds
        await asyncio.sleep(15)
