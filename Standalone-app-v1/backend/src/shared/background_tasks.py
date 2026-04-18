import asyncio
import logging
from datetime import datetime, timezone
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from httpx import TimeoutException, HTTPStatusError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.domain.entities import Ticker
from src.market_data.services.yahoo_service import YahooFinanceService
from src.shared.services.sse_manager import sse_manager
from src.shared.infra.config import get_settings

logger = logging.getLogger(__name__)

def is_retryable_http_error(exc: Exception) -> bool:
    """Ritorna True se l'errore è un timeout o un HTTP status error 429/5xx."""
    if isinstance(exc, TimeoutException):
        return True
    if isinstance(exc, HTTPStatusError):
        status = exc.response.status_code
        if status == 429 or status >= 500:
            return True
    return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception), # Catch generic first, then filter
    before_sleep=lambda retry_state: logger.warning(f"Retrying Yahoo fetch after error: {retry_state.outcome.exception()}"),
)
async def _fetch_yahoo_v8_latest_price(symbol: str) -> dict | None:
    """
    Helper function per recuperare l'ultimo prezzo e il relativo timestamp usando esattamente 
    i module di query Yahoo v8 (finance/chart).
    Supporta retry automatici su timeout o 429/5xx.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1m"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            if is_retryable_http_error(e):
                raise
            logger.error(f"Non-retryable Yahoo error for {symbol}: {e}")
            return None

        data = response.json()
        
        results = data.get("chart", {}).get("result", [])
        if not results:
            return None
            
        timestamps = results[0].get("timestamp", [])
        quote = results[0].get("indicators", {}).get("quote", [])
        if not timestamps or not quote:
            return None
            
        # Recuperiamo gli ultimi dati validi sfogliando gli array a ritroso se l'ultimo minuto non fosse formattato (null values)
        closes = quote[0].get("close", [])
        for i in range(len(closes)-1, -1, -1):
            if closes[i] is not None:
                return {
                    "price": float(closes[i]), 
                    "timestamp": timestamps[i] # Epoch scaturito dal server v8 Yahoo
                }
        return None

async def start_price_loop(app_state: dict):
    """
    Continuous background loop that fetches active symbols from DB, 
    refreshes live prices ticker by ticker (Yahoo v8), evaluates take-profit/stop-loss,
    closes estimates if targets are reached saving the exact candle timestamp, 
    and broadcasts updates via SSE.
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
                        latest_data = await _fetch_yahoo_v8_latest_price(symbol)
                        
                        if latest_data is not None:
                            curr_price = latest_data["price"]
                            candle_epoch = latest_data["timestamp"]
                            candle_time = datetime.fromtimestamp(candle_epoch, tz=timezone.utc).replace(tzinfo=None)

                            # 3. Valutazione Stop-Loss e Take-Profit nel db_session (isolato)
                            async with db_session_factory() as inner_session:
                                changes_made = False
                                for est in estimates:
                                    # FIX 1: Retrieve estimate using .get() instead of detached .add()
                                    est_in_inner = await inner_session.get(Estimate, est.id)
                                    if not est_in_inner or est_in_inner.status != EstimateStatus.OPEN:
                                        continue

                                    new_state = est_in_inner.status.value
                                    
                                    # Logica target hit / stop loss (long only)
                                    if est_in_inner.target_price and curr_price >= est_in_inner.target_price:
                                        est_in_inner.status = EstimateStatus.CLOSED_WIN
                                    elif est_in_inner.stop_loss_price and curr_price <= est_in_inner.stop_loss_price:
                                        est_in_inner.status = EstimateStatus.CLOSED_LOSS

                                    # Se lo stato è cambiato compiliamo i dati attuali
                                    if est_in_inner.status.value != new_state:
                                        est_in_inner.exit_price = curr_price
                                        est_in_inner.closed_at = candle_time # FIX timestamp candela Yahoo
                                        est_in_inner.realized_pnl = curr_price - est_in_inner.start_price
                                        changes_made = True
                                        
                                        logger.info(f"Estimate {est_in_inner.id} closed as {est_in_inner.status} at {curr_price} (Time: {candle_time})")

                                    # 4. SSE Event Emitter (Aggiornamento status real-time per frontend)
                                    await sse_manager.broadcast({
                                        "type": "estimate_update",
                                        "estimate_id": str(est_in_inner.id),
                                        "new_state": est_in_inner.status.value,
                                        "trigger_price": curr_price
                                    })
                                
                                # FIX 2: await commit fuori dal loop dei singoli est, scrivendo tutte le mod del ticker scattato
                                if changes_made:
                                    await inner_session.commit()

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
