import pytest
from datetime import date, timedelta

from src.market_data.api.dependencies import get_market_data_provider

@pytest.mark.e2e
async def test_yahoo_current_price(provider):
    """Real API call to Yahoo Finance for current price."""
    p = provider
    # Removed skip logic to see full error
    price = await p.get_current_price("AAPL")
    assert price.close > 0
    assert "yahoo" in price.source

@pytest.mark.e2e
async def test_yahoo_historical(provider):
    """Real historical data from Yahoo."""
    p = provider
    try:
        history = await p.get_historical_prices(
            "AAPL",
            date.today() - timedelta(days=7),
            date.today(),
            interval='1d'
        )
    except Exception as e:
        pytest.skip(f"Yahoo provider unavailable in this environment: {e}")
    assert len(history) >= 1
