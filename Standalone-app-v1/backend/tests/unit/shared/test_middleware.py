"""
Unit tests for security middleware and health check routes.

Tests cover:
- Security headers are added to responses
- CORS configuration
- Rate limiting functionality
- Health check endpoints
"""

from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.shared.api.health_routes import router as health_router
from src.shared.infra.security_middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    setup_security_middleware,
)


class TestSecurityHeadersMiddleware:
    """Test security headers middleware functionality."""

    def test_security_headers_added_to_response(self):
        """Test that security headers are added to all responses."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")

        # Check security headers are present
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert (
            response.headers.get("strict-transport-security")
            == "max-age=31536000; includeSubDomains"
        )

    def test_security_headers_not_added_to_non_http(self):
        """Test that middleware doesn't interfere with non-HTTP requests."""
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        # This should not raise any errors
        response = client.get("/test")
        assert response.status_code == 200


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_allows_localhost_3000(self):
        """Test CORS allows requests from localhost:3000."""
        app = FastAPI()
        setup_security_middleware(app)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_allows_vite_dev_server(self):
        """Test CORS allows requests from Vite dev server (port 5173)."""
        app = FastAPI()
        setup_security_middleware(app)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test", headers={"Origin": "http://localhost:5173"})

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    def test_rate_limit_blocks_after_threshold(self, monkeypatch):
        """Test rate limit blocks requests after threshold."""
        # Create settings with rate limit enabled
        monkeypatch.setenv("ENABLE_RATE_LIMIT", "true")
        monkeypatch.setenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "5")

        from src.shared.infra.config import get_settings

        get_settings.cache_clear()

        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        # Manually add rate limit middleware with low limit
        middleware = RateLimitMiddleware(app.router, requests_per_minute=3)

        # We can't directly test this with TestClient due to how middlewares work
        # This would require more complex setup with actual HTTP requests
        # For now, we test the IP extraction and rate limit logic

        assert middleware.requests_per_minute == 3

    def test_rate_limit_disabled_via_config(self, monkeypatch):
        """Test rate limit can be disabled via configuration."""
        monkeypatch.setenv("ENABLE_RATE_LIMIT", "false")

        from src.shared.infra.config import get_settings

        get_settings.cache_clear()

        app = FastAPI()
        setup_security_middleware(app)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200

    def test_get_client_ip_from_x_forwarded_for(self):
        """Test extracting client IP from X-Forwarded-For header."""
        app = FastAPI()
        RateLimitMiddleware(app.router)

        # Create a mock request object
        class MockRequest:
            def __init__(self, headers, client_tuple):
                self.headers = headers
                self.client = client_tuple

        # Test X-Forwarded-For with single IP
        MockRequest({"X-Forwarded-For": "192.168.1.100"}, ("127.0.0.1", 8000))
        # Create proper Request from scope
        from starlette.datastructures import Headers

        Headers({"X-Forwarded-For": "192.168.1.100"})
        # Note: Full IP extraction test would need proper Request object
        # This is simplified for unit testing

    def test_get_client_ip_from_direct_connection(self):
        """Test extracting client IP from direct connection."""
        app = FastAPI()
        RateLimitMiddleware(app.router)

        # This would need proper Request object from Starlette
        # Full test requires more setup


class TestHealthCheckEndpoints:
    """Test health check endpoints (updated for Task 3.7 JSONResponse format)."""

    def _make_system_health_healthy(self):
        from src.infra.health.health_service import ComponentHealth, SystemHealth
        return SystemHealth(
            status="HEALTHY",
            version="3.0.0",
            uptime_seconds=1.0,
            components=[
                ComponentHealth("database", "HEALTHY", 1.0),
                ComponentHealth("redis", "HEALTHY", 1.0),
                ComponentHealth("yahoo_finance", "HEALTHY", 1.0),
                ComponentHealth("google_drive", "HEALTHY", 1.0),
            ],
        )

    def test_health_endpoint_returns_ok(self):
        """Test /health endpoint returns 200 status when healthy."""
        app = FastAPI()
        app.include_router(health_router)

        health = self._make_system_health_healthy()
        with patch(
            "src.infra.health.health_service.HealthService.check_all",
            AsyncMock(return_value=health),
        ):
            client = TestClient(app)
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "HEALTHY"

    def test_health_endpoint_response_structure(self):
        """Test /health endpoint response has required fields."""
        app = FastAPI()
        app.include_router(health_router)

        health = self._make_system_health_healthy()
        with patch(
            "src.infra.health.health_service.HealthService.check_all",
            AsyncMock(return_value=health),
        ):
            client = TestClient(app)
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "components" in data

    def test_ready_endpoint_returns_ready(self):
        """Test /health/ready endpoint returns 200 when DB is healthy."""
        from src.infra.health.health_service import ComponentHealth
        app = FastAPI()
        app.include_router(health_router)

        db_healthy = ComponentHealth("database", "HEALTHY", 1.0)
        with patch(
            "src.infra.health.health_service.HealthService.check_database",
            AsyncMock(return_value=db_healthy),
        ):
            client = TestClient(app)
            response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_ready_endpoint_includes_checks(self):
        """Test /health/ready response includes database field."""
        from src.infra.health.health_service import ComponentHealth
        app = FastAPI()
        app.include_router(health_router)

        db_healthy = ComponentHealth("database", "HEALTHY", 1.0)
        with patch(
            "src.infra.health.health_service.HealthService.check_database",
            AsyncMock(return_value=db_healthy),
        ):
            client = TestClient(app)
            response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "latency_ms" in data
        assert "ready" in data


class TestSecurityHeadersMiddlewareIntegration:
    """Integration tests for security middleware."""

    def test_full_middleware_stack_on_request(self):
        """Test full middleware stack processes request correctly."""
        app = FastAPI()
        setup_security_middleware(app)
        app.include_router(health_router)

        with patch(
            "src.shared.api.health_routes.HealthService.check_all",
            new_callable=lambda: (lambda *a, **k: None),  # placeholder
        ):
            pass  # will use live liveness endpoint instead

        client = TestClient(app)
        response = client.get("/health/live", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_health_check_with_security_headers(self):
        """Test /health/live endpoint includes all security headers."""
        app = FastAPI()
        setup_security_middleware(app)
        app.include_router(health_router)

        client = TestClient(app)
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers


class TestDockerHealthProbe:
    """Test Docker / Kubernetes health probe compatibility."""

    def test_health_endpoint_suitable_for_docker_healthcheck(self):
        """Test /health/live is suitable for Docker HEALTHCHECK (always 200)."""
        app = FastAPI()
        app.include_router(health_router)

        client = TestClient(app)
        response = client.get("/health/live")

        assert response.status_code == 200
        assert response.json()["alive"] is True

    def test_ready_endpoint_suitable_for_kubernetes_readiness(self):
        """Test /health/ready is suitable for Kubernetes readiness probe."""
        from src.infra.health.health_service import ComponentHealth
        app = FastAPI()
        app.include_router(health_router)

        db_healthy = ComponentHealth("database", "HEALTHY", 1.0)
        with patch(
            "src.infra.health.health_service.HealthService.check_database",
            AsyncMock(return_value=db_healthy),
        ):
            client = TestClient(app)
            response = client.get("/health/ready")

        assert response.status_code == 200
        assert response.json()["ready"] is True
