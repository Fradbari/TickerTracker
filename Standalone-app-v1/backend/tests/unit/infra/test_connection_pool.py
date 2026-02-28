"""
Unit tests for Task 3.10 — Connection Pooling Ottimizzato.

Tests cover:
- Settings pool defaults and overrides
- database.py get_pool_status() function
- Prometheus pool Gauge metrics
- update_pool_metrics() helper
- /health/pool endpoint
- /health includes connection_pool section
- /metrics includes pool gauges
- API_KEY_EXEMPT_PATHS includes /health/pool

Strategy
--------
- Settings tests use ``Settings(_env_file=None, ...)`` to avoid .env pollution.
- Pool-status tests mock ``engine.pool`` to avoid needing a running DB.
- Metric tests use isolated registries where possible, or reset global Gauges.
- Endpoint tests use a minimal FastAPI TestClient.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.shared.infra.config import Settings, get_settings


# ---------------------------------------------------------------------------
# Settings pool defaults
# ---------------------------------------------------------------------------

class TestPoolSettings:
    """Verify pool-related fields in Settings."""

    def test_pool_defaults(self, monkeypatch):
        """Default pool settings match Task 3.10 specification."""
        for key in ["DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_POOL_TIMEOUT",
                     "DB_POOL_RECYCLE", "DB_POOL_PRE_PING"]:
            monkeypatch.delenv(key, raising=False)
        s = Settings(_env_file=None)
        assert s.DB_POOL_SIZE == 5
        assert s.DB_MAX_OVERFLOW == 10
        assert s.DB_POOL_TIMEOUT == 30
        assert s.DB_POOL_RECYCLE == 1800
        assert s.DB_POOL_PRE_PING is True

    def test_pool_size_override(self):
        """Pool size can be overridden via constructor (simulates env var)."""
        s = Settings(_env_file=None, DB_POOL_SIZE=10)
        assert s.DB_POOL_SIZE == 10

    def test_max_overflow_override(self):
        s = Settings(_env_file=None, DB_MAX_OVERFLOW=20)
        assert s.DB_MAX_OVERFLOW == 20

    def test_pool_timeout_override(self):
        s = Settings(_env_file=None, DB_POOL_TIMEOUT=60)
        assert s.DB_POOL_TIMEOUT == 60

    def test_pool_recycle_override(self):
        s = Settings(_env_file=None, DB_POOL_RECYCLE=900)
        assert s.DB_POOL_RECYCLE == 900

    def test_pool_pre_ping_disabled(self):
        s = Settings(_env_file=None, DB_POOL_PRE_PING=False)
        assert s.DB_POOL_PRE_PING is False

    def test_health_pool_in_exempt_paths(self, monkeypatch):
        """``/health/pool`` must be in API_KEY_EXEMPT_PATHS by default."""
        for key in ["API_KEY_EXEMPT_PATHS"]:
            monkeypatch.delenv(key, raising=False)
        s = Settings(_env_file=None)
        assert "/health/pool" in s.API_KEY_EXEMPT_PATHS


# ---------------------------------------------------------------------------
# get_pool_status()
# ---------------------------------------------------------------------------

class TestGetPoolStatus:
    """Verify get_pool_status returns the right dict shape."""

    def test_returns_expected_keys(self):
        """get_pool_status must return all 5 documented keys."""
        mock_pool = MagicMock()
        mock_pool.size.return_value = 5
        mock_pool.checkedin.return_value = 3
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 0
        mock_pool.invalid.return_value = 0

        with patch("src.shared.infra.database.engine") as mock_engine:
            mock_engine.pool = mock_pool
            from src.shared.infra.database import get_pool_status
            status = get_pool_status()

        expected_keys = {"pool_size", "checked_in", "checked_out", "overflow", "invalid"}
        assert set(status.keys()) == expected_keys

    def test_returns_correct_values(self):
        """Values from pool proxy are forwarded correctly."""
        mock_pool = MagicMock()
        mock_pool.size.return_value = 10
        mock_pool.checkedin.return_value = 7
        mock_pool.checkedout.return_value = 3
        mock_pool.overflow.return_value = 1
        mock_pool.invalid.return_value = 0

        with patch("src.shared.infra.database.engine") as mock_engine:
            mock_engine.pool = mock_pool
            from src.shared.infra.database import get_pool_status
            status = get_pool_status()

        assert status["pool_size"] == 10
        assert status["checked_in"] == 7
        assert status["checked_out"] == 3
        assert status["overflow"] == 1
        assert status["invalid"] == 0


# ---------------------------------------------------------------------------
# update_pool_metrics()
# ---------------------------------------------------------------------------

class TestUpdatePoolMetrics:
    """Verify Prometheus Gauge refresh."""

    def test_update_sets_gauges(self):
        from src.infra.metrics.metrics import (
            update_pool_metrics,
            db_pool_checked_out,
            db_pool_checked_in,
            db_pool_overflow,
            db_pool_size,
        )

        fake_status = {
            "pool_size": 5,
            "checked_in": 4,
            "checked_out": 1,
            "overflow": 0,
            "invalid": 0,
        }
        with patch("src.shared.infra.database.get_pool_status", return_value=fake_status):
            update_pool_metrics()

        # Read gauge values via internal _value
        assert db_pool_size._value.get() == 5.0
        assert db_pool_checked_in._value.get() == 4.0
        assert db_pool_checked_out._value.get() == 1.0
        assert db_pool_overflow._value.get() == 0.0

    def test_update_does_not_raise_on_error(self):
        """update_pool_metrics must swallow all exceptions."""
        from src.infra.metrics.metrics import update_pool_metrics

        with patch(
            "src.shared.infra.database.get_pool_status",
            side_effect=RuntimeError("boom"),
        ):
            # Should NOT raise
            update_pool_metrics()


# ---------------------------------------------------------------------------
# /health/pool endpoint
# ---------------------------------------------------------------------------

class TestHealthPoolEndpoint:
    """Verify the dedicated /health/pool endpoint."""

    def _make_app(self) -> FastAPI:
        from src.shared.api.health_routes import router
        app = FastAPI()
        app.include_router(router)
        return app

    def test_returns_200(self):
        """Endpoint always returns HTTP 200."""
        with patch("src.shared.api.health_routes.get_pool_status", return_value={
            "pool_size": 5, "checked_in": 5, "checked_out": 0,
            "overflow": 0, "invalid": 0,
        }):
            client = TestClient(self._make_app())
            resp = client.get("/health/pool")
        assert resp.status_code == 200

    def test_returns_correct_shape(self):
        """Response body contains all pool status fields."""
        fake = {
            "pool_size": 5, "checked_in": 3, "checked_out": 2,
            "overflow": 1, "invalid": 0,
        }
        with patch("src.shared.api.health_routes.get_pool_status", return_value=fake):
            client = TestClient(self._make_app())
            body = client.get("/health/pool").json()
        for key in ("pool_size", "checked_in", "checked_out", "overflow", "invalid"):
            assert key in body

    def test_returns_error_on_failure(self):
        """If pool check fails, the response includes an error key but stays 200."""
        with patch(
            "src.shared.api.health_routes.get_pool_status",
            side_effect=RuntimeError("unreachable"),
        ):
            client = TestClient(self._make_app())
            resp = client.get("/health/pool")
        assert resp.status_code == 200
        assert "error" in resp.json()


# ---------------------------------------------------------------------------
# /health includes connection_pool
# ---------------------------------------------------------------------------

class TestHealthFullIncludesPool:
    """Verify /health response includes connection_pool dict."""

    def _make_app(self) -> FastAPI:
        from src.shared.api.health_routes import router
        app = FastAPI()
        app.include_router(router)
        return app

    def test_health_response_has_connection_pool_key(self):
        """Full /health check includes connection_pool section."""
        fake_pool = {
            "pool_size": 5, "checked_in": 5, "checked_out": 0,
            "overflow": 0, "invalid": 0,
        }
        with patch("src.shared.api.health_routes.get_pool_status", return_value=fake_pool), \
             patch("src.shared.api.health_routes.HealthService") as MockHS:
            from src.infra.health.health_service import SystemHealth, ComponentHealth
            MockHS.return_value.check_all.return_value = SystemHealth(
                status="HEALTHY",
                version="3.0.0",
                uptime_seconds=42.0,
                components=[
                    ComponentHealth(name="database", status="HEALTHY", latency_ms=1.0),
                ],
            )
            # Make check_all awaitable
            import asyncio

            async def _fake_check_all():
                return SystemHealth(
                    status="HEALTHY",
                    version="3.0.0",
                    uptime_seconds=42.0,
                    components=[
                        ComponentHealth(name="database", status="HEALTHY", latency_ms=1.0),
                    ],
                )

            MockHS.return_value.check_all = _fake_check_all

            client = TestClient(self._make_app())
            body = client.get("/health").json()

        assert "connection_pool" in body
        assert body["connection_pool"]["pool_size"] == 5


# ---------------------------------------------------------------------------
# QueuePool import in database.py
# ---------------------------------------------------------------------------

class TestDatabaseModuleImports:
    """Verify database.py exports and imports."""

    def test_no_null_pool_import(self):
        """NullPool must NOT be imported in database.py."""
        import importlib
        import src.shared.infra.database as db_mod
        source = importlib.util.find_spec("src.shared.infra.database")
        # Read actual source to verify NullPool is not imported
        if source and source.origin:
            with open(source.origin, "r", encoding="utf-8") as f:
                content = f.read()
            assert "NullPool" not in content, "NullPool import should have been removed"

    def test_no_explicit_poolclass(self):
        """poolclass= should NOT appear in database.py (async engine auto-uses AsyncAdaptedQueuePool)."""
        import importlib
        source = importlib.util.find_spec("src.shared.infra.database")
        if source and source.origin:
            with open(source.origin, "r", encoding="utf-8") as f:
                content = f.read()
            assert "poolclass=" not in content, (
                "poolclass= should not be set; async engine uses AsyncAdaptedQueuePool by default"
            )

    def test_pool_params_present(self):
        """All 5 pool parameters must appear in database.py source."""
        import importlib
        source = importlib.util.find_spec("src.shared.infra.database")
        if source and source.origin:
            with open(source.origin, "r", encoding="utf-8") as f:
                content = f.read()
            for param in ("pool_size", "max_overflow", "pool_timeout", "pool_recycle", "pool_pre_ping"):
                assert param in content, f"{param} missing from database.py"

    def test_get_pool_status_callable(self):
        """get_pool_status is importable and callable."""
        from src.shared.infra.database import get_pool_status
        assert callable(get_pool_status)

    def test_pool_status_returns_dict(self):
        """get_pool_status returns a dict (even with default engine)."""
        from src.shared.infra.database import get_pool_status
        result = get_pool_status()
        assert isinstance(result, dict)
        assert "pool_size" in result
