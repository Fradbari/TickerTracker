import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.shared.infra.config import get_settings
from src.shared.utils.http_utils import is_retryable_http_error
from src.market_data.schemas.search import FinnhubSymbolResult

logger = logging.getLogger(__name__)
settings = get_settings()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda rs: logger.warning(f"Retrying Finnhub fetch after error: {rs.outcome.exception()}"),
)
async def get_quote(symbol: str) -> dict | None:
    """Fetch real-time quote for a symbol from Finnhub."""
    api_key = settings.FINNHUB_API_KEY.get_secret_value() if settings.FINNHUB_API_KEY else ""
    if not api_key:
        logger.error("FINNHUB_API_KEY non configurata.")
        return None

    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException:
            from fastapi import HTTPException
            raise HTTPException(status_code=504, detail="Gateway Timeout from Finnhub")
        except Exception as e:
            if is_retryable_http_error(e):
                raise
            logger.error(f"Errore non recuperabile Finnhub quote per {symbol}: {e}")
            return None

        # Return the parsed payload
        # Finnhub quote response mapped: c=current, h=high, l=low, o=open, pc=prev close, t=timestamp
        return response.json()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda rs: logger.warning(f"Retrying Finnhub candles fetch after error: {rs.outcome.exception()}"),
)
async def get_candles(symbol: str, resolution: str, from_ts: int, to_ts: int) -> list[dict]:
    """Fetch historical OHLCV candles from Finnhub."""
    api_key = settings.FINNHUB_API_KEY.get_secret_value() if settings.FINNHUB_API_KEY else ""
    if not api_key:
        logger.error("FINNHUB_API_KEY non configurata.")
        return []

    url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution={resolution}&from={from_ts}&to={to_ts}&token={api_key}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException:
            from fastapi import HTTPException
            raise HTTPException(status_code=504, detail="Gateway Timeout from Finnhub")
        except Exception as e:
            if is_retryable_http_error(e):
                raise
            logger.error(f"Errore non recuperabile Finnhub candles per {symbol}: {e}")
            return []

        data = response.json()
        if data.get("s") != "ok":
            return []
            
        candles = []
        for i in range(len(data.get("t", []))):
            candles.append({
                "timestamp": data["t"][i],
                "open": data["o"][i],
                "high": data["h"][i],
                "low": data["l"][i],
                "close": data["c"][i],
                "volume": data["v"][i],
            })
        return candles

async def symbol_lookup(query: str) -> list[FinnhubSymbolResult]:
    """Cerca su Finnhub simboli ticker matchanti (autocomplete)."""
    api_key = settings.FINNHUB_API_KEY.get_secret_value() if settings.FINNHUB_API_KEY else ""
    if not api_key:
        logger.warning("FINNHUB_API_KEY non configurata. Ricerca fallback vuota.")
        return []

    url = f"https://finnhub.io/api/v1/search?q={query}&token={api_key}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException:
            from fastapi import HTTPException
            raise HTTPException(status_code=504, detail="Gateway Timeout from Finnhub")
        except Exception as e:
            logger.error(f"Errore ricerca simbolo su Finnhub per query '{query}': {e}")
            return []

        data = response.json()
        count = data.get("count", 0)
        if count == 0:
            return []

        results = []
        valid_types = {"Common Stock", "ETP", "ADR"}
        exact_query = query.strip().lower()

        for item in data.get("result", []):
            sym = item.get("symbol", "")
            itype = item.get("type", "")
            desc = item.get("description", "")
            
            if not sym:
                continue
                
            if itype in valid_types or sym.lower() == exact_query:
                results.append(FinnhubSymbolResult(
                    symbol=sym,
                    description=desc,
                    type=itype,
                    mic_code=item.get("mic")
                ))
                
        return results
