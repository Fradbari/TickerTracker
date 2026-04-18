import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import httpx
from src.market_data.candle_service import backfill_candles_on_startup, _fetch_yahoo_v8_candles
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.domain.entities import Ticker, Candle

pytestmark = pytest.mark.asyncio

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Error", request=MagicMock(), response=self)

@patch("src.market_data.candle_service.httpx.AsyncClient.get")
async def test_fetch_yahoo_v8_candles_success(mock_get):
    """Testa se preleva correttamente le candele proxy di Yahoo v8."""
    mock_get.return_value = MockResponse({
        "chart": {
            "result": [{
                "timestamp": [1700000000, 1700086400],
                "indicators": {
                    "quote": [{
                        "open": [10.0, 11.0],
                        "high": [12.0, 13.0],
                        "low": [9.0, 10.0],
                        "close": [11.0, 12.0],
                        "volume": [1000, 2000]
                    }]
                }
            }]
        }
    })
    
    symbol = "TSLA"
    start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    candles = await _fetch_yahoo_v8_candles(symbol, start_time)
    
    assert len(candles) == 2
    assert candles[0]["open"] == 10.0
    assert candles[1]["close"] == 12.0

@patch("src.market_data.candle_service.AsyncSessionLocal")
@patch("src.market_data.candle_service._fetch_yahoo_v8_candles")
@patch("src.market_data.candle_service.sse_manager.broadcast", new_callable=AsyncMock)
async def test_backfill_candles_on_startup_empty(mock_broadcast, mock_fetch, mock_session_maker):
    """Testa il backfill se non ci sono estimates aperti."""
    # Imposta un mock session che non restuituisce risultati
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result
    
    mock_session_maker.return_value.__aenter__.return_value = mock_session
    
    await backfill_candles_on_startup()
    mock_fetch.assert_not_called()
    mock_broadcast.assert_not_called()
