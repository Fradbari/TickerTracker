"""
Tests for src/infra/health/health_service.py  (Task 3.7)
=========================================================

Strategy:
- All external I/O is mocked.  No real DB / Redis / Yahoo / Drive calls.
- ``AsyncSessionLocal`` is patched inside health_service (lazy import).
- ``redis.asyncio.from_url`` is patched at module level.
- ``yfinance.Ticker`` is patched at module level.
- ``GoogleDriveClient`` is patched inside health_service (lazy import).
- HTTP-layer tests use FastAPI ``TestClient`` + ``AsyncClient``.

Coverage:
13 tests grouped by component:
  - Database (2)
  - Redis (2)
  - Yahoo Finance (2)
  - Google Drive (3)
  - check_all / SystemHealth (2)
  - HTTP endpoints via health_routes (2)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.infra.health.health_service import (
    ComponentHealth,
    HealthService,
    SystemHealth,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_mock_session(*, raise_exc: Exception | None = None) -> AsyncMock:
    """Build an AsyncMock that mimics an async SQLAlchemy session context manager."""
    session = AsyncMock()
    if raise_exc is not None:
        session.execute.side_effect = raise_exc
    else:
        session.execute.return_value = MagicMock()

    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=session)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm


@pytest.fixture()
def _settings_redis_url(monkeypatch):
    """Patch get_settings to return a fake REDIS_URL."""
    fake_settings = MagicMock()
    fake_settings.REDIS_URL = "redis://localhost:6379/0"
    monkeypatch.setattr(
        "src.infra.health.health_service.HealthService.check_redis.__func__",
        None,
        raising=False,
    )
    return fake_settings


# ---------------------------------------------------------------------------
# Database checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_database_healthy():
    """SELECT 1 succeeds → status HEALTHY."""
    mock_cm = _make_mock_session()

    with (
        patch("src.infra.health.health_service.AsyncSessionLocal", return_value=mock_cm),
        patch("sqlalchemy.text", return_value="SELECT 1"),
    ):
        result = await HealthService().check_database()

    assert result.name == "database"
    assert result.status == "HEALTHY"
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_check_database_unhealthy():
    """Exception during SELECT 1 → status UNHEALTHY."""
    mock_cm = _make_mock_session(raise_exc=ConnectionRefusedError("db down"))

    with (
        patch("src.infra.health.health_service.AsyncSessionLocal", return_value=mock_cm),
        patch("sqlalchemy.text", return_value="SELECT 1"),
    ):
        result = await HealthService().check_database()

    assert result.status == "UNHEALTHY"
    assert "db down" in result.message


# ---------------------------------------------------------------------------
# Redis checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_redis_healthy():
    """Redis ping succeeds → status HEALTHY."""
    mock_redis = AsyncMock()
    mock_redis.ping = AsyncMock(return_value=True)
    mock_redis.aclose = AsyncMock()

    fake_settings = MagicMock()
    fake_settings.REDIS_URL = "redis://localhost:6379/0"

    with (
        patch(
            "src.infra.health.health_service.HealthService.check_redis",
            wraps=None,
        ),
    ):
        pass  # marker — actual patch below

    # Patch the lazy import inside check_redis
    with (
        patch("src.infra.health.health_service.get_settings", return_value=fake_settings),
        patch("src.infra.health.health_service.aioredis.from_url", return_value=mock_redis),
    ):
        result = await HealthService().check_redis()

    assert result.name == "redis"
    assert result.status == "HEALTHY"
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_check_redis_degraded():
    """Redis ping raises → status DEGRADED (non-critical)."""
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = ConnectionRefusedError("redis down")
    mock_redis.aclose = AsyncMock()

    fake_settings = MagicMock()
    fake_settings.REDIS_URL = "redis://localhost:6379/0"

    with (
        patch("src.infra.health.health_service.get_settings", return_value=fake_settings),
        patch("src.infra.health.health_service.aioredis.from_url", return_value=mock_redis),
    ):
        result = await HealthService().check_redis()

    assert result.status == "DEGRADED"
    assert "redis down" in result.message


# ---------------------------------------------------------------------------
# Yahoo Finance checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_yahoo_healthy():
    """yfinance returns price > 0 → status HEALTHY."""
    mock_ticker = MagicMock()
    mock_ticker.fast_info.get.return_value = 190.5

    with patch("src.infra.health.health_service.yf.Ticker", return_value=mock_ticker):
        result = await HealthService().check_yahoo()

    assert result.name == "yahoo_finance"
    assert result.status == "HEALTHY"
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_check_yahoo_degraded_zero_price():
    """yfinance returns price == 0 → status DEGRADED."""
    mock_ticker = MagicMock()
    mock_ticker.fast_info.get.return_value = 0

    with patch("src.infra.health.health_service.yf.Ticker", return_value=mock_ticker):
        result = await HealthService().check_yahoo()

    assert result.status == "DEGRADED"
    assert "0" in result.message or "price" in result.message.lower()


# ---------------------------------------------------------------------------
# Google Drive checks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_drive_not_configured():
    """DRIVE_FOLDER_ID empty → DEGRADED with 'not configured' message."""
    fake_settings = MagicMock()
    fake_settings.DRIVE_FOLDER_ID = ""
    fake_settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value.return_value = "{}"

    with patch("src.infra.health.health_service.get_settings", return_value=fake_settings):
        result = await HealthService().check_drive()

    assert result.name == "google_drive"
    assert result.status == "DEGRADED"
    assert "not configured" in result.message.lower() or "DRIVE_FOLDER_ID" in result.message


@pytest.mark.asyncio
async def test_check_drive_healthy():
    """Drive list_files succeeds → status HEALTHY."""
    fake_settings = MagicMock()
    fake_settings.DRIVE_FOLDER_ID = "folder-abc"
    fake_settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value.return_value = "{}"

    mock_drive = AsyncMock()
    mock_drive.list_files = AsyncMock(return_value=[{"id": "file1"}])

    with (
        patch("src.infra.health.health_service.get_settings", return_value=fake_settings),
        patch(
            "src.infra.health.health_service.GoogleDriveClient",
            return_value=mock_drive,
        ),
    ):
        result = await HealthService().check_drive()

    assert result.name == "google_drive"
    assert result.status == "HEALTHY"


@pytest.mark.asyncio
async def test_check_drive_degraded():
    """Drive list_files raises → status DEGRADED."""
    fake_settings = MagicMock()
    fake_settings.DRIVE_FOLDER_ID = "folder-abc"
    fake_settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value.return_value = "{}"

    mock_drive = AsyncMock()
    mock_drive.list_files.side_effect = Exception("drive error")

    with (
        patch("src.infra.health.health_service.get_settings", return_value=fake_settings),
        patch(
            "src.infra.health.health_service.GoogleDriveClient",
            return_value=mock_drive,
        ),
    ):
        result = await HealthService().check_drive()

    assert result.status == "DEGRADED"
    assert "drive error" in result.message


# ---------------------------------------------------------------------------
# check_all / SystemHealth aggregation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_all_healthy_when_all_pass():
    """All components healthy → system HEALTHY."""
    svc = HealthService()
    ComponentHealth(name="x", status="HEALTHY", latency_ms=1.0)

    with (
        patch.object(svc, "check_database", AsyncMock(return_value=ComponentHealth("database", "HEALTHY", 1.0))),
        patch.object(svc, "check_redis", AsyncMock(return_value=ComponentHealth("redis", "HEALTHY", 1.0))),
        patch.object(svc, "check_yahoo", AsyncMock(return_value=ComponentHealth("yahoo_finance", "HEALTHY", 1.0))),
        patch.object(svc, "check_drive", AsyncMock(return_value=ComponentHealth("google_drive", "HEALTHY", 1.0))),
    ):
        result = await svc.check_all()

    assert isinstance(result, SystemHealth)
    assert result.status == "HEALTHY"
    assert len(result.components) == 4
    assert result.is_ready is True


@pytest.mark.asyncio
async def test_check_all_unhealthy_when_db_down():
    """DB UNHEALTHY → system UNHEALTHY; is_ready False."""
    svc = HealthService()

    with (
        patch.object(svc, "check_database", AsyncMock(return_value=ComponentHealth("database", "UNHEALTHY", 50.0, "conn refused"))),
        patch.object(svc, "check_redis", AsyncMock(return_value=ComponentHealth("redis", "HEALTHY", 1.0))),
        patch.object(svc, "check_yahoo", AsyncMock(return_value=ComponentHealth("yahoo_finance", "HEALTHY", 1.0))),
        patch.object(svc, "check_drive", AsyncMock(return_value=ComponentHealth("google_drive", "HEALTHY", 1.0))),
    ):
        result = await svc.check_all()

    assert result.status == "UNHEALTHY"
    assert result.is_ready is False


# ---------------------------------------------------------------------------
# HTTP endpoint tests (health_routes)
# ---------------------------------------------------------------------------


@pytest.fixture()
def _health_app() -> FastAPI:
    """Minimal FastAPI app with only the health router mounted."""
    from src.shared.api.health_routes import router

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_live_endpoint_always_200(_health_app: FastAPI):
    """GET /health/live → 200, alive=True, no external calls needed."""
    async with AsyncClient(
        transport=ASGITransport(app=_health_app), base_url="http://test"
    ) as client:
        resp = await client.get("/health/live")

    assert resp.status_code == 200
    data = resp.json()
    assert data["alive"] is True
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_ready_endpoint_503_when_db_down(_health_app: FastAPI):
    """GET /health/ready → 503 when database is UNHEALTHY."""
    db_failure = ComponentHealth("database", "UNHEALTHY", 50.0, "conn refused")

    with patch(
        "src.infra.health.health_service.HealthService.check_database",
        AsyncMock(return_value=db_failure),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=_health_app), base_url="http://test"
        ) as client:
            resp = await client.get("/health/ready")

    assert resp.status_code == 503
    data = resp.json()
    assert data["ready"] is False
    assert data["database"] == "UNHEALTHY"
