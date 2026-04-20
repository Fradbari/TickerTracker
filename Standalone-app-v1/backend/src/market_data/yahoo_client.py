import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.shared.utils.http_utils import is_retryable_http_error

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda rs: logger.warning(f"Retrying Yahoo single price fetch for {rs.outcome.exception()}"),
)
async def get_current_price(symbol: str) -> float | None:
    """
    Yahoo single-price validation per Task 4/2A.
    Ritorna il `regularMarketPrice` prelevandolo dal nodo "meta" di Yahoo API v8.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            if is_retryable_http_error(e):
                raise
            logger.error(f"Errore Yahoo chart validation per {symbol}: {e}")
            return None

        # Risposta in JSON
        data = response.json()
        results = data.get("chart", {}).get("result", [])
        if not results:
            return None
            
        # Estraiamo il nodo 'meta'
        meta = results[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        
        if price is not None:
            return float(price)
            
        return None
        
        
async def validate_symbol_on_yahoo(symbol: str) -> bool:
    """Valida se un ticker esiste interrogando la v8 e sperando di ottenere un prezzo."""
    val = await get_current_price(symbol)
    return val is not None
