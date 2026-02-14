"""
PyTest configuration and fixtures for backend tests.

Provides shared fixtures for database, services, repositories, and test data.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infra.database import AsyncSessionLocal
from src.market_data.domain.entities import Ticker
from src.market_data.repositories.market_data_repository import (
    MarketDataRepository,
    MarketDataRow,
)
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.estimates.repositories.estimate_event_repository import EstimateEventRepository
from src.estimates.services.estimate_service import EstimateService
from src.estimates.services.estimate_history_service import EstimateHistoryService


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session


# ============================================================================
# REPOSITORY FIXTURES
# ============================================================================

@pytest.fixture
async def market_data_repository() -> MarketDataRepository:
    """Provide a MarketDataRepository instance."""
    return MarketDataRepository(AsyncSessionLocal)


@pytest.fixture
async def estimate_repository() -> EstimateRepository:
    """Provide an EstimateRepository instance."""
    return EstimateRepository(AsyncSessionLocal)


@pytest.fixture
async def estimate_event_repository() -> EstimateEventRepository:
    """Provide an EstimateEventRepository instance."""
    return EstimateEventRepository(AsyncSessionLocal)


# ============================================================================
# SERVICE FIXTURES
# ============================================================================

@pytest.fixture
async def estimate_service(
    estimate_repository: EstimateRepository,
    estimate_event_repository: EstimateEventRepository,
) -> EstimateService:
    """Provide an EstimateService instance."""
    return EstimateService(estimate_repository, estimate_event_repository)


@pytest.fixture
async def history_service(
    estimate_repository: EstimateRepository,
    estimate_event_repository: EstimateEventRepository,
) -> EstimateHistoryService:
    """Provide an EstimateHistoryService instance."""
    return EstimateHistoryService(estimate_repository, estimate_event_repository)


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
async def test_ticker(db_session: AsyncSession) -> Ticker:
    """
    Create and persist a test ticker.
    
    Generates a unique ticker symbol for each test to avoid collisions.
    """
    unique_id = str(uuid4())[:8].upper()
    symbol = f"TST{unique_id[:6]}"
    
    ticker = Ticker(
        id=uuid4(),
        symbol=symbol,
        name=f"Test Company {unique_id}",
        exchange="NASDAQ",
        currency="USD",
        asset_type="stock",
    )
    
    db_session.add(ticker)
    await db_session.commit()
    await db_session.refresh(ticker)
    
    return ticker


@pytest.fixture
async def test_ticker_with_market_data(
    test_ticker: Ticker,
    market_data_repository: MarketDataRepository,
) -> Ticker:
    """
    Create a test ticker with market data.
    
    Adds OHLCV data for the current date.
    """
    rows = [
        MarketDataRow(
            date=datetime.now(timezone.utc).date(),
            open=Decimal("100.00"),
            high=Decimal("105.00"),
            low=Decimal("95.00"),
            close=Decimal("100.00"),
            volume=1000000,
            data_source="test",
        )
    ]
    
    await market_data_repository.upsert_daily(test_ticker.id, rows)
    
    return test_ticker


@pytest.fixture
def ticker_id(test_ticker: Ticker) -> str:
    """Provide the test ticker ID as a string (for compatibility with existing tests)."""
    return str(test_ticker.id)


@pytest.fixture
async def estimate_id(
    test_ticker_with_market_data: Ticker,
    estimate_service: EstimateService,
) -> str:
    """
    Create a test estimate and return its ID.
    
    Creates an estimate for the test ticker that can be used in tests.
    """
    from src.estimates.schemas.commands import CreateEstimateCommand
    
    cmd = CreateEstimateCommand(
        ticker_id=test_ticker_with_market_data.id,
        direction="LONG",
        target_profit_percent=Decimal("10.0"),
        stop_loss_percent=Decimal("5.0"),
        ai_model="gpt-4",
    )
    
    estimate = await estimate_service.create_estimate(cmd)
    
    return str(estimate.id)


@pytest.fixture
def start_time() -> datetime:
    """Provide a timestamp for the start of a test."""
    return datetime.now(timezone.utc)
