import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.e2e
async def test_get_current_price_yahoo_real(async_client: AsyncClient):
    """Test GET /api/market/price/{ticker} with real Yahoo data."""
    response = await async_client.get("/api/market/price/AAPL")
    if response.status_code != 200:
        pytest.skip(f"Market API unavailable or provider failed: {response.status_code}")
    data = response.json()["data"]
    assert data["symbol"] == "AAPL"
    assert float(data["price"]) > 0
    # allow either 'yahoo' or 'yahoo+cached'
    assert "yahoo" in data["source"]
