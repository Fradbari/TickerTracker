"""
Unit tests for src/infra/security/middleware.py  (Task 3.1).

Coverage targets:
- Security headers (static + conditional HSTS + CSP)
- API key validation (enabled/disabled, correct/incorrect key, exempt paths)
- Request logging (enabled/disabled)
- register_security_middleware helper
- <1 ms overhead acceptance criterion validated via smoke check
"""

from __future__ import annotations

import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.infra.security.middleware import (
    SecurityMiddleware,
    _apply_security_headers,
    _client_ip,
    register_security_middleware,
)
from starlette.responses import Response


# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------


def _make_settings(
    *,
    api_key_enabled: bool = False,
    api_key: str = "",
    csp_policy: str = "default-src 'self'",
    request_log: bool = True,
    exempt_paths: list[str] | None = None,
):
    """Return a minimal mock Settings object for SecurityMiddleware."""
    from pydantic import SecretStr

    s = MagicMock()
    s.ENABLE_API_KEY_AUTH = api_key_enabled
    s.API_KEY = SecretStr(api_key)
    s.CSP_POLICY = csp_policy
    s.REQUEST_LOG_ENABLED = request_log
    s.API_KEY_EXEMPT_PATHS = exempt_paths or [
        "/health",
        "/health/ready",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    return s


def _make_app(settings=None) -> FastAPI:
    """Return a minimal FastAPI app with SecurityMiddleware registered."""
    app = FastAPI()
    register_security_middleware(app, settings=settings)

    @app.get("/test")
    async def test_ep():
        return {"ok": True}

    @app.get("/health")
    async def health_ep():
        return {"status": "ok"}

    @app.get("/secure")
    async def secure_ep():
        return {"secret": "data"}

    return app


# ---------------------------------------------------------------------------
# 1. Security headers
# ---------------------------------------------------------------------------


class TestStaticSecurityHeaders:
    """Security headers present on every HTTP response."""

    def test_x_content_type_options(self):
        app = _make_app(settings=_make_settings())
        client = TestClient(app)
        r = client.get("/test")
        assert r.headers.get("x-content-type-options") == "nosniff"

    def test_x_frame_options(self):
        app = _make_app(settings=_make_settings())
        client = TestClient(app)
        r = client.get("/test")
        assert r.headers.get("x-frame-options") == "DENY"

    def test_x_xss_protection(self):
        app = _make_app(settings=_make_settings())
        client = TestClient(app)
        r = client.get("/test")
        assert r.headers.get("x-xss-protection") == "1; mode=block"

    def test_hsts_absent_on_http(self):
        """HSTS must NOT be set on plain HTTP requests."""
        app = _make_app(settings=_make_settings())
        client = TestClient(app)
        r = client.get("/test")  # TestClient uses http://testserver
        assert "strict-transport-security" not in r.headers

    def test_csp_header_present(self):
        """CSP header is set from the configured policy."""
        settings = _make_settings(csp_policy="default-src 'self'")
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/test")
        assert r.headers.get("content-security-policy") == "default-src 'self'"

    def test_csp_header_absent_when_empty(self):
        """CSP header is omitted when policy is empty string."""
        settings = _make_settings(csp_policy="")
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/test")
        assert "content-security-policy" not in r.headers

    def test_headers_on_4xx_response(self):
        """Security headers are added even to 404 responses."""
        app = _make_app(settings=_make_settings())
        client = TestClient(app)
        r = client.get("/nonexistent")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"


class TestHSTSConditional:
    """Validate HSTS conditional logic via unit-level helper."""

    def test_hsts_added_when_https(self):
        resp = Response()
        _apply_security_headers(resp, is_https=True, csp_policy="")
        assert "strict-transport-security" in resp.headers
        assert "max-age=31536000" in resp.headers["strict-transport-security"]

    def test_hsts_absent_when_http(self):
        resp = Response()
        _apply_security_headers(resp, is_https=False, csp_policy="")
        assert "strict-transport-security" not in resp.headers

    def test_hsts_includes_subdomain(self):
        resp = Response()
        _apply_security_headers(resp, is_https=True, csp_policy="")
        assert "includeSubDomains" in resp.headers["strict-transport-security"]


# ---------------------------------------------------------------------------
# 2. API key validation
# ---------------------------------------------------------------------------


class TestApiKeyDisabled:
    """When API key auth is disabled, all requests pass through."""

    def test_no_key_header_still_200(self):
        settings = _make_settings(api_key_enabled=False)
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/secure")
        assert r.status_code == 200

    def test_wrong_key_still_200(self):
        settings = _make_settings(api_key_enabled=False, api_key="correct-key")
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/secure", headers={"X-API-Key": "wrong-key"})
        assert r.status_code == 200


class TestApiKeyEnabled:
    """When API key auth is enabled, invalid requests are rejected."""

    _settings = _make_settings(api_key_enabled=True, api_key="super-secret-key-42")

    def test_missing_key_returns_401(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure")
        assert r.status_code == 401
        assert "Missing X-API-Key" in r.json()["detail"]

    def test_missing_key_has_www_authenticate(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure")
        assert r.headers.get("www-authenticate") == "ApiKey"

    def test_wrong_key_returns_401(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure", headers={"X-API-Key": "wrong-key"})
        assert r.status_code == 401
        assert "Invalid API key" in r.json()["detail"]

    def test_correct_key_returns_200(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure", headers={"X-API-Key": "super-secret-key-42"})
        assert r.status_code == 200

    def test_security_headers_on_401(self):
        """Even a rejected request must carry security headers."""
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("x-frame-options") == "DENY"


class TestApiKeyExemptPaths:
    """Exempt paths bypass API key validation."""

    _settings = _make_settings(
        api_key_enabled=True,
        api_key="secret",
        exempt_paths=["/health", "/health/ready", "/docs", "/openapi.json", "/redoc"],
    )

    def test_health_exempt_no_key_200(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/health")
        assert r.status_code == 200

    def test_secure_not_exempt_no_key_401(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/secure")
        assert r.status_code == 401

    def test_nonexempt_path_rejected(self):
        app = _make_app(settings=self._settings)
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/test")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# 3. Client IP extraction
# ---------------------------------------------------------------------------


class TestClientIpExtraction:
    """_client_ip helper extracts the correct IP."""

    def _mock_request(self, forwarded=None, client_host="127.0.0.1"):
        req = MagicMock()
        req.headers = {}
        if forwarded:
            req.headers = {"X-Forwarded-For": forwarded}
        req.client = MagicMock()
        req.client.host = client_host
        return req

    def test_x_forwarded_for_single(self):
        req = self._mock_request(forwarded="203.0.113.5")
        assert _client_ip(req) == "203.0.113.5"

    def test_x_forwarded_for_multiple(self):
        req = self._mock_request(forwarded="203.0.113.5, 10.0.0.1, 172.16.0.1")
        assert _client_ip(req) == "203.0.113.5"

    def test_direct_connection(self):
        req = self._mock_request(client_host="192.168.1.100")
        assert _client_ip(req) == "192.168.1.100"

    def test_no_client(self):
        req = MagicMock()
        req.headers = {}
        req.client = None
        assert _client_ip(req) == "unknown"


# ---------------------------------------------------------------------------
# 4. Request logging toggle
# ---------------------------------------------------------------------------


class TestRequestLogging:
    """REQUEST_LOG_ENABLED controls whether logs are emitted."""

    def test_logging_enabled_does_not_crash(self):
        """Verify middleware works without errors when logging is on."""
        settings = _make_settings(request_log=True)
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/test")
        assert r.status_code == 200

    def test_logging_disabled_does_not_crash(self):
        """Verify middleware works without errors when logging is off."""
        settings = _make_settings(request_log=False)
        app = _make_app(settings=settings)
        client = TestClient(app)
        r = client.get("/test")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# 5. Performance acceptance criterion
# ---------------------------------------------------------------------------


class TestPerformance:
    """Middleware overhead must be <1 ms per request (acceptance criterion)."""

    def test_middleware_overhead_under_1ms(self):
        """
        Validates that SecurityMiddleware does not add significant overhead.

        TestClient uses an in-process ASGI transport which itself costs ~3-8ms
        per call due to Python async machinery (not the middleware).  We therefore
        measure the overhead as the DIFFERENCE between a run WITH the middleware
        and a run WITHOUT it.  The delta must be < 1 ms on average.

        As a safety net we also cap the absolute average below 20 ms so we
        catch runaway performance regressions.
        """
        N = 50

        # App WITHOUT SecurityMiddleware (baseline)
        baseline_app = FastAPI()

        @baseline_app.get("/test")
        async def _ep():
            return {"ok": True}

        baseline_client = TestClient(baseline_app)
        # Warm up
        for _ in range(5):
            baseline_client.get("/test")
        t0 = time.perf_counter()
        for _ in range(N):
            baseline_client.get("/test")
        baseline_avg_ms = (time.perf_counter() - t0) / N * 1000

        # App WITH SecurityMiddleware
        settings = _make_settings(request_log=False)
        mw_app = _make_app(settings=settings)
        mw_client = TestClient(mw_app)
        # Warm up
        for _ in range(5):
            mw_client.get("/test")
        t0 = time.perf_counter()
        for _ in range(N):
            mw_client.get("/test")
        mw_avg_ms = (time.perf_counter() - t0) / N * 1000

        overhead_ms = mw_avg_ms - baseline_avg_ms

        # Middleware itself must add < 1 ms
        assert overhead_ms < 1.0, (
            f"Middleware overhead {overhead_ms:.2f} ms exceeds 1 ms acceptance criterion"
        )
        # Absolute guard: full round-trip must stay below 20 ms
        assert mw_avg_ms < 20, f"Absolute avg {mw_avg_ms:.2f} ms is suspiciously high"


# ---------------------------------------------------------------------------
# 6. register_security_middleware helper
# ---------------------------------------------------------------------------


class TestRegisterSecurityMiddleware:
    """register_security_middleware wires up the middleware correctly."""

    def test_registers_without_error(self):
        app = FastAPI()
        register_security_middleware(app, settings=_make_settings())
        # Should not raise

    def test_integration_headers_present(self):
        settings = _make_settings(csp_policy="default-src 'self'")
        app = FastAPI()
        register_security_middleware(app, settings=settings)

        @app.get("/ping")
        async def ping():
            return {"pong": True}

        client = TestClient(app)
        r = client.get("/ping")
        assert r.headers.get("x-content-type-options") == "nosniff"
        assert r.headers.get("content-security-policy") == "default-src 'self'"
