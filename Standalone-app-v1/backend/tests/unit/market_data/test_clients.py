import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from src.market_data.finnhub_client import get_quote, get_candles
from src.market_data.yahoo_client import get_current_price

@pytest.mark.asyncio
async def test_finnhub_get_quote(mocker):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"c": 150.0, "h": 155.0, "l": 149.0, "pc": 145.0, "t": 1612345678}
    
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = mock_response
    
    # Mock return context manager
    mock_client_class = mocker.patch("httpx.AsyncClient")
    mock_client_class.return_value.__aenter__.return_value = mock_client_instance
    
    # Mock settings
    mocker.patch("src.market_data.finnhub_client.get_settings").return_value.FINNHUB_API_KEY.get_secret_value.return_value = "TEST_API_KEY"

    result = await get_quote("AAPL")
    
    assert result is not None
    assert result["c"] == 150.0
    mock_client_instance.get.assert_called_once()
    assert "token=TEST_API_KEY" in mock_client_instance.get.call_args[0][0]

@pytest.mark.asyncio
async def test_finnhub_get_candles(mocker):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "s": "ok",
        "t": [1612345678, 1612345679],
        "o": [140.0, 141.0],
        "h": [142.0, 143.0],
        "l": [139.0, 140.0],
        "c": [141.0, 142.0],
        "v": [1000, 2000]
    }
    
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = mock_response
    
    mock_client_class = mocker.patch("httpx.AsyncClient")
    mock_client_class.return_value.__aenter__.return_value = mock_client_instance
    
    mocker.patch("src.market_data.finnhub_client.get_settings").return_value.FINNHUB_API_KEY.get_secret_value.return_value = "TEST_API_KEY"

    candles = await get_candles("AAPL", "D", 1612340000, 1612350000)
    
    assert len(candles) == 2
    assert candles[0]["open"] == 140.0
    assert candles[1]["close"] == 142.0

@pytest.mark.asyncio
async def test_yahoo_get_current_price(mocker):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "chart": {
            "result": [
                {
                    "meta": {
                        "regularMarketPrice": 160.5
                    }
                }
            ]
        }
    }
    
    mock_client_instance = AsyncMock()
    mock_client_instance.get.return_value = mock_response
    
    mock_client_class = mocker.patch("httpx.AsyncClient")
    mock_client_class.return_value.__aenter__.return_value = mock_client_instance
    
    result = await get_current_price("AAPL")
    
    assert result == 160.5
    mock_client_instance.get.assert_called_once()
    assert "AAPL" in mock_client_instance.get.call_args[0][0]