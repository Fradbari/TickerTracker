import os
import pytest
from httpx import AsyncClient
from src.main import app
from src.shared.infra.config import get_settings, Settings
from src.market_data.api.dependencies import get_market_data_provider
from src.market_data.domain.providers import MarketDataProvider

# Load .env.e2e if present
_env = os.path.join(os.path.dirname(__file__), '..', '..', '.env.e2e')
if os.path.exists(_env):
    from dotenv import load_dotenv
    load_dotenv(_env)

@pytest.fixture(scope='session')
def settings() -> Settings:
    return get_settings()

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def provider():
    # Return the DI provider instance used by the app
    p = get_market_data_provider()
    # If provider is a dependency generator, call it
    if hasattr(p, '__call__'):
        p = p()
    return p
