import asyncio
import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.shared.infra.database import Base, get_db

# SQLite In-Memory Database for Unit and Integration tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def sqlite_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(autouse=True)
def override_db_session_factory(sqlite_engine):
    """Monkeypatch AsyncSessionLocal globally to use SQLite memory during tests."""
    from src.shared.infra import database
    TestSessionLocal = async_sessionmaker(bind=sqlite_engine, expire_on_commit=False, class_=AsyncSession)
    original = database.AsyncSessionLocal
    database.AsyncSessionLocal = TestSessionLocal
    yield
    database.AsyncSessionLocal = original

@pytest.fixture
async def async_session(sqlite_engine) -> AsyncGenerator[AsyncSession, None]:
    TestSessionLocal = async_sessionmaker(bind=sqlite_engine, expire_on_commit=False, class_=AsyncSession)
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def mock_yahoo_provider():
    return AsyncMock()

@pytest.fixture
def mock_drive_client():
    return AsyncMock()

@pytest.fixture
async def test_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
