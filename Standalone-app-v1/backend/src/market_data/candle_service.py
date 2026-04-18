import asyncio
import logging
from datetime import datetime, timezone, timedelta
import httpx
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from httpx import TimeoutException, HTTPStatusError

from src.shared.infra.database import AsyncSessionLocal
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.domain.entities import Ticker, Candle
from src.shared.services.sse_manager import sse_manager

logger = logging.getLogger(__name__)

def is_retryable_http_error(exc: Exception) -> bool:
    if isinstance(exc, TimeoutException):
        return True
    if isinstance(exc, HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda rs: logger.warning(f"Retrying Yahoo backfill proxy: {rs.outcome.exception()}"),
)
async def _fetch_yahoo_v8_candles(symbol: str, start_time: datetime) -> list[dict]:
    """Recupera le candele storiche giornaliere tramite Yahoo v8, partendo da start_time fino ad oggi."""
    period1 = int(start_time.timestamp())
    period2 = int(datetime.now(timezone.utc).timestamp())
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={period1}&period2={period2}&interval=1d"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            if is_retryable_http_error(e):
                raise
            logger.error(f"Non-retryable Yahoo error for backfill {symbol}: {e}")
            return []

        data = response.json()
        results = data.get("chart", {}).get("result", [])
        if not results:
            return []
            
        timestamps = results[0].get("timestamp", [])
        quote = results[0].get("indicators", {}).get("quote", [])
        if not timestamps or not quote:
            return []
            
        candles = []
        q = quote[0]
        for i, ts in enumerate(timestamps):
            o = q.get("open", [])[i]
            h = q.get("high", [])[i]
            l = q.get("low", [])[i]
            c = q.get("close", [])[i]
            v = q.get("volume", [])[i]
            
            if o is not None and c is not None:
                candles.append({
                    "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None),
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": int(v) if v is not None else 0
                })
        
        # Ordiniamo cronologicamente dal più vecchio al più recente
        return sorted(candles, key=lambda c: c["timestamp"])

async def backfill_candles_on_startup() -> None:
    """
    Task 4: All'avvio, recupera le stime attive e scarica le candele mancanti per i rispettivi ticker.
    Rivaluta stop-loss e take-profit per evitare gap causati da offline del server.
    Utilizza logic UPSERT/Ignore per inserire candele ed emette segnali SSE completati.
    """
    logger.info("Starting backfill for active estimates candles...")
    
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Estimate)
            .where(Estimate.status == EstimateStatus.OPEN)
            .where(Estimate.is_deleted == False)
            .options(selectinload(Estimate.ticker))
        )
        result = await session.execute(stmt)
        active_estimates = result.scalars().all()
    
    if not active_estimates:
        logger.info("No active estimates to backfill.")
        return

    # Organizziamo le stime per ticker_id
    ticker_map = {}
    for est in active_estimates:
        if est.ticker:
            ticker_map.setdefault(est.ticker.id, []).append(est)

    # Elaboariamo ciascun ticker
    for ticker_id, estimates in ticker_map.items():
        symbol = estimates[0].ticker.symbol
        try:
            async with AsyncSessionLocal() as session:
                # Determiniamo l'ultima candela disponibile; se nessuna scendiamo 30 giorni
                last_candle_stmt = select(func.max(Candle.timestamp_start)).where(Candle.ticker_id == ticker_id)
                last_time_result = await session.execute(last_candle_stmt)
                last_time = last_time_result.scalar()

                if not last_time:
                    last_time = datetime.now() - timedelta(days=30)
                else:
                    # Iniziamo a cercare dal giorno successivo per evitare ricaricamenti massivi
                    last_time = last_time + timedelta(seconds=1)

                logger.info(f"Backfilling {symbol} dal {last_time}...")
                new_candles_data = await _fetch_yahoo_v8_candles(symbol, last_time)

                if not new_candles_data:
                    continue
                
                # Salvataggio/upsert delle nuove candele e order execution
                for c_data in new_candles_data:
                    c_time = c_data["timestamp"]
                    
                    # Verifichiamo se esiste per logica upsert
                    exists_stmt = select(Candle).where(Candle.ticker_id == ticker_id, Candle.timestamp_start == c_time)
                    exists_run = await session.execute(exists_stmt)
                    if not exists_run.scalar_one_or_none():
                        new_candle = Candle(
                            ticker_id=ticker_id,
                            timestamp_start=c_time,
                            open_price=c_data["open"],
                            high_price=c_data["high"],
                            low_price=c_data["low"],
                            close_price=c_data["close"],
                            volume=c_data["volume"]
                        )
                        session.add(new_candle)
                    
                    # Valutazione sequenziale su ciascun estimate in base al high/low della candela
                    for est in estimates:
                        est_in_db = await session.get(Estimate, est.id)
                        if est_in_db and est_in_db.status == EstimateStatus.OPEN:
                            closed_state = None
                            
                            if est_in_db.target_price and c_data["high"] >= est_in_db.target_price:
                                closed_state = EstimateStatus.CLOSED_WIN
                            elif est_in_db.stop_loss_price and c_data["low"] <= est_in_db.stop_loss_price:
                                closed_state = EstimateStatus.CLOSED_LOSS
                                
                            if closed_state:
                                est_in_db.status = closed_state
                                est_in_db.exit_price = c_data["close"]  # Approssimazione di base sul close per target gap
                                est_in_db.closed_at = c_time
                                est_in_db.realized_pnl = float(est_in_db.exit_price) - float(est_in_db.start_price)
                                
                                logger.info(f"Backfill hit per {est_in_db.id} su {symbol} al timestamp {c_time}. Stato: {closed_state.value}")
                                
                                await sse_manager.broadcast({
                                    "type": "estimate_update",
                                    "estimate_id": str(est_in_db.id),
                                    "new_state": closed_state.value,
                                    "trigger_price": float(est_in_db.exit_price)
                                })
                
                await session.commit()
                
                # Inviamo l'evidenza del backfill completato per aggiornare la UI
                for est in estimates:
                    await sse_manager.broadcast({
                        "type": "backfill_complete",
                        "estimate_id": str(est.id),
                        "symbol": symbol
                    })
                    
        except Exception as e:
            logger.error(f"Errore non fatale durante il backfill per {symbol}: {e}")
            continue

    logger.info("Backfill completed.")
