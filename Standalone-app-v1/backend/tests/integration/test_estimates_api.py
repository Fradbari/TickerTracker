import pytest
import uuid
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.market_data.domain.entities import Ticker
from src.market_data.domain.market_data import MarketData
from src.estimates.domain.entities import Estimate, EstimateStatus, Direction
from src.main import app

# Apply integration marker to all tests in this file
pytestmark = pytest.mark.integration


@pytest.fixture
def override_yahoo_provider(mock_yahoo_provider):
    """Override dependency to use the mocked provider."""
    from src.market_data.api.dependencies import get_market_data_provider
    app.dependency_overrides[get_market_data_provider] = lambda: mock_yahoo_provider
    yield mock_yahoo_provider
    app.dependency_overrides.clear()


@pytest.fixture
async def setup_ticker_with_price(async_session: AsyncSession) -> Ticker:
    """Insert a valid ticker and its market data into the clean database."""
    ticker_id = uuid.uuid4()
    ticker = Ticker(
        id=ticker_id,
        symbol="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        asset_type="stock",
    )
    async_session.add(ticker)
    
    from datetime import date
    
    market_data = MarketData(
        ticker_id=ticker_id,
        date=date.today(),
        open=Decimal("100.00"),
        high=Decimal("105.00"),
        low=Decimal("95.00"),
        close=Decimal("100.00"),
        volume=1000
    )
    async_session.add(market_data)
    
    await async_session.commit()
    await async_session.refresh(ticker)
    return ticker


@pytest.fixture
async def setup_estimate(async_session: AsyncSession, setup_ticker_with_price: Ticker) -> Estimate:
    """Insert a valid estimate for testing GET, PATCH, DELETE."""
    estimate = Estimate(
        id=uuid.uuid4(),
        ticker_id=setup_ticker_with_price.id,
        user_id=uuid.uuid4(),
        direction=Direction.LONG,
        start_price=Decimal("100.00"),
        target_price=Decimal("110.00"),
        stop_loss_price=Decimal("95.00"),
        target_profit_percent=Decimal("10.0"),
        stop_loss_percent=Decimal("5.0"),
        status=EstimateStatus.OPEN,
    )
    async_session.add(estimate)
    await async_session.commit()
    await async_session.refresh(estimate)
    return estimate


class TestEstimatesAPI:
    
    async def test_create_estimate_valid(
        self, 
        test_client: AsyncClient, 
        setup_ticker_with_price: Ticker,
        override_yahoo_provider
    ):
        payload = {
            "ticker_id": str(setup_ticker_with_price.id),
            "direction": "LONG",
            "target_profit_percent": 10.0,
            "stop_loss_percent": 5.0
        }
        
        response = await test_client.post("/api/estimates", json=payload)
        
        assert response.status_code == 201, response.json()
        data = response.json()
        assert data["success"] is True, data
        assert data["data"]["estimate"]["direction"] == "LONG"
        assert data["data"]["estimate"]["start_price"] == "100.000000"
        assert data["data"]["estimate"]["target_price"] == "110.000000"
        assert data["data"]["estimate"]["stop_loss_price"] == "95.000000"
        assert data["data"]["estimate"]["status"] == "OPEN"

    async def test_create_estimate_invalid_ticker(self, test_client: AsyncClient, override_yahoo_provider):
        payload = {
            "ticker_id": str(uuid.uuid4()),
            "direction": "LONG",
            "target_profit_percent": 10.0,
            "stop_loss_percent": 5.0
        }
        
        response = await test_client.post("/api/estimates", json=payload)
        
        # Endpoint returns 200 with success=False and Error schema
        data = response.json()
        assert data["success"] is False, data
        assert data["error"]["code"] == "TICKER_NOT_FOUND", data

    async def test_create_estimate_validation_error(self, test_client: AsyncClient, setup_ticker_with_price: Ticker, override_yahoo_provider):
        payload = {
            "ticker_id": str(setup_ticker_with_price.id),
            "direction": "LONG",
            "target_profit_percent": -10.0,  # Invalid
            "stop_loss_percent": 5.0
        }
        
        response = await test_client.post("/api/estimates", json=payload)
        
        # Pydantic validation error returns 422
        assert response.status_code == 422

    async def test_list_estimates_empty(self, test_client: AsyncClient):
        response = await test_client.get("/api/estimates")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["items"]) == 0
        assert data["data"]["total"] == 0

    async def test_list_estimates_with_filters(self, test_client: AsyncClient, setup_estimate: Estimate):
        # Fetch specifying the precise status
        response = await test_client.get("/api/estimates?status=OPEN")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True, data
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == str(setup_estimate.id)
        
        # Fetch specifying a wrong status
        response_empty = await test_client.get("/api/estimates?status=CLOSED_WIN")
        assert len(response_empty.json()["data"]["items"]) == 0

    async def test_get_estimate_existing(self, test_client: AsyncClient, setup_estimate: Estimate):
        response = await test_client.get(f"/api/estimates/{setup_estimate.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True, data
        assert data["data"]["id"] == str(setup_estimate.id)
        assert data["data"]["status"] == "OPEN"

    async def test_get_estimate_not_found(self, test_client: AsyncClient):
        fake_id = uuid.uuid4()
        response = await test_client.get(f"/api/estimates/{fake_id}")
        
        data = response.json()
        assert data["success"] is False, data
        assert data["error"]["code"] == "ESTIMATE_NOT_FOUND", data

    async def test_update_estimate(self, test_client: AsyncClient, setup_estimate: Estimate):
        payload = {
            "target_profit_percent": 20.0,
            "stop_loss_percent": 10.0
        }
        
        response = await test_client.patch(f"/api/estimates/{setup_estimate.id}", json=payload)
        
        data = response.json()
        assert data["success"] is True, data
        assert data["data"]["estimate"]["target_price"] == "120.000000"
        assert data["data"]["estimate"]["stop_loss_price"] == "90.000000"

    async def test_close_estimate(self, test_client: AsyncClient, setup_estimate: Estimate):
        payload = {
            "exit_price": 115.00,
            "reason": "Closed early to secure profits"
        }
        
        response = await test_client.request("DELETE", f"/api/estimates/{setup_estimate.id}", json=payload)
        
        data = response.json()
        assert data["success"] is True, data
        assert data["data"]["status"] == "CLOSED_WIN"
        
        # Verify it actually changed via GET
        get_resp = await test_client.get(f"/api/estimates/{setup_estimate.id}")
        assert get_resp.json()["data"]["status"] == "CLOSED_WIN"
        assert get_resp.json()["data"]["exit_price"] == "115.000000"
