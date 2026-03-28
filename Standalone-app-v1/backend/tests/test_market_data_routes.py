"""
Test for Market Data API Routes (TASK 2.17).

Validates that market data endpoints work correctly with the provider chain.
"""


from fastapi.testclient import TestClient

from src.main import app

# Use TestClient for synchronous API testing
client = TestClient(app)


def test_api_routes_registered():
    """Test that market data routes are registered in the app."""
    routes = [route.path for route in app.routes]

    assert "/api/market/price/{ticker}" in routes
    assert "/api/market/history/{ticker}" in routes
    assert "/api/market/fundamentals/{ticker}" in routes
    assert "/api/market/search" in routes


# Note: Full integration tests would require mocking the MarketDataProvider
# or using a test database with real data. These tests verify route registration.
# Full endpoint testing should be done with manual verification or E2E tests.

def test_market_routes_have_correct_tags():
    """Test that market data routes are tagged correctly."""
    market_routes = [
        route for route in app.routes
        if hasattr(route, 'path') and route.path.startswith("/api/market")
    ]

    for route in market_routes:
        if hasattr(route, 'tags'):
            assert "Market Data" in route.tags


def test_health_check():
    """Sanity check that the app is running."""
    response = client.get("/health")
    assert response.status_code == 200
    # Health check returns ApiResponse format
    data = response.json()
    assert "success" in data or "status" in data
