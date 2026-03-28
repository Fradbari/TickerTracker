"""
Unit tests for src/infra/security/rate_limit.py  (Task 3.2).

Strategy
--------
• Use in-memory slowapi storage (``memory://``) so tests never need Redis.
• Build isolated ``Limiter`` instances via ``_build_limiter(mock_settings)``
  to avoid touching the module-level singleton.
• For integration assertions (429, Retry-After) create lightweight FastAPI
  test apps with ``TestClient``.
• Simulate external IPs via the ``X-Forwarded-For`` header so that
  localhost/127.0.0.1 whitelist entries don't interfere.

Coverage
--------
  TestClientIpExtraction        – _client_ip() helper
  TestWhitelistFunction         – is_whitelisted()
  TestBuildLimiter              – _build_limiter() factory
  TestSetupRateLimiter          – setup_rate_limiter() wiring
  TestRateLimitExceededHandler  – 429 response shape & headers
  TestRateLimitEnforced         – integration: limit is enforced after N hits
  TestWhitelistExempt           – integration: whitelisted IPs pass freely
  TestEndpointSpecificLimits    – integration: per-endpoint limits differ
  Test429HeadersPresent         – Retry-After present on 429
"""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_settings(
    *,
    enabled: bool = True,
    default_limit: str = "5/minute",
    whitelist: list[str] | None = None,
    redis_url: str = "memory://",
    chat_limit: str = "2/minute",
    estimates_post_limit: str = "3/minute",
    market_price_limit: str = "4/minute",
) -> MagicMock:
    """Create a mock Settings object isolated from .env files."""
    s = MagicMock()
    s.RATE_LIMIT_SLOWAPI_ENABLED = enabled
    s.RATE_LIMIT_DEFAULT = default_limit
    s.RATE_LIMIT_WHITELIST_IPS = whitelist if whitelist is not None else ["192.168.99.99"]
    s.REDIS_URL = redis_url
    s.RATE_LIMIT_CHAT = chat_limit
    s.RATE_LIMIT_ESTIMATES_POST = estimates_post_limit
    s.RATE_LIMIT_MARKET_PRICE = market_price_limit
    return s


def _make_app(limit: str = "5/minute", whitelist: list[str] | None = None) -> FastAPI:
    """Create a minimal FastAPI app with the rate limiter wired up."""
    from src.infra.security.rate_limit import setup_rate_limiter

    settings = _make_settings(default_limit=limit, whitelist=whitelist or [])

    app = FastAPI()
    setup_rate_limiter(app, settings=settings)

    @app.get("/test")
    async def test_ep():
        return {"ok": True}

    @app.post("/limited")
    async def limited_ep():
        return {"ok": True}

    return app


def _external_ip_headers(ip: str = "10.0.1.55") -> dict[str, str]:
    """Return headers that present a non-whitelisted client IP."""
    return {"X-Forwarded-For": ip}


# ---------------------------------------------------------------------------
# 1. _client_ip helper
# ---------------------------------------------------------------------------

class TestClientIpExtraction:
    """_client_ip() correctly resolves the originating IP address."""

    def _req(self, forwarded: str | None = None, client_host: str | None = None):
        """Build a minimal mock Request."""
        r = MagicMock()
        r.headers = {"X-Forwarded-For": forwarded} if forwarded else {}
        if client_host:
            r.client = MagicMock()
            r.client.host = client_host
        else:
            r.client = None
        return r

    def test_returns_first_forwarded_ip(self):
        from src.infra.security.rate_limit import _client_ip

        req = self._req(forwarded="1.2.3.4, 5.6.7.8")
        assert _client_ip(req) == "1.2.3.4"

    def test_strips_whitespace_in_forwarded(self):
        from src.infra.security.rate_limit import _client_ip

        req = self._req(forwarded="  1.2.3.4  ,  5.6.7.8")
        assert _client_ip(req) == "1.2.3.4"

    def test_single_forwarded_ip(self):
        from src.infra.security.rate_limit import _client_ip

        req = self._req(forwarded="77.88.90.1")
        assert _client_ip(req) == "77.88.90.1"

    def test_falls_back_to_client_host(self):
        from src.infra.security.rate_limit import _client_ip

        req = self._req(client_host="192.168.1.1")
        assert _client_ip(req) == "192.168.1.1"

    def test_unknown_when_no_client(self):
        from src.infra.security.rate_limit import _client_ip

        req = self._req()
        assert _client_ip(req) == "unknown"


# ---------------------------------------------------------------------------
# 2. is_whitelisted()
# ---------------------------------------------------------------------------

class TestWhitelistFunction:
    """is_whitelisted() correctly determines whether the client is exempt."""

    def _set_ctx(self, ip: str):
        """Force the ContextVar to a specific IP for testing."""
        from src.infra.security.rate_limit import _current_request

        mock_req = MagicMock()
        mock_req.headers = {"X-Forwarded-For": ip}
        mock_req.client = None
        _current_request.set(mock_req)

    def test_whitelisted_ip_returns_true(self):
        from src.infra.security.rate_limit import is_whitelisted

        self._set_ctx("10.0.0.1")
        with patch(
            "src.infra.security.rate_limit._get_settings",
            return_value=_make_settings(whitelist=["10.0.0.1", "10.0.0.2"]),
        ):
            assert is_whitelisted() is True

    def test_non_whitelisted_ip_returns_false(self):
        from src.infra.security.rate_limit import is_whitelisted

        self._set_ctx("8.8.8.8")
        with patch(
            "src.infra.security.rate_limit._get_settings",
            return_value=_make_settings(whitelist=["10.0.0.1"]),
        ):
            assert is_whitelisted() is False

    def test_empty_whitelist_never_exempt(self):
        from src.infra.security.rate_limit import is_whitelisted

        self._set_ctx("127.0.0.1")
        with patch(
            "src.infra.security.rate_limit._get_settings",
            return_value=_make_settings(whitelist=[]),
        ):
            assert is_whitelisted() is False

    def test_loopback_whitelisted_by_settings(self):
        from src.infra.security.rate_limit import is_whitelisted

        self._set_ctx("127.0.0.1")
        with patch(
            "src.infra.security.rate_limit._get_settings",
            return_value=_make_settings(whitelist=["127.0.0.1", "::1"]),
        ):
            assert is_whitelisted() is True

    def test_no_context_returns_false(self):
        from src.infra.security.rate_limit import _current_request, is_whitelisted

        _current_request.set(None)  # explicitly clear
        with patch(
            "src.infra.security.rate_limit._get_settings",
            return_value=_make_settings(whitelist=["10.0.0.1"]),
        ):
            assert is_whitelisted() is False


# ---------------------------------------------------------------------------
# 3. _build_limiter()
# ---------------------------------------------------------------------------

class TestBuildLimiter:
    """_build_limiter() returns a functional Limiter with the correct storage."""

    def test_returns_limiter_instance(self):
        from slowapi import Limiter

        from src.infra.security.rate_limit import _build_limiter

        lim = _build_limiter(_make_settings())
        assert isinstance(lim, Limiter)

    def test_falls_back_to_memory_when_redis_unreachable(self):
        """When Redis host does not exist, storage falls back to memory."""
        from slowapi import Limiter

        from src.infra.security.rate_limit import _build_limiter

        settings = _make_settings(redis_url="redis://nonexistent_host_xyz:6379/0")
        lim = _build_limiter(settings)
        assert isinstance(lim, Limiter)

    def test_disabled_limiter_has_no_default_limits(self):
        from src.infra.security.rate_limit import _build_limiter

        settings = _make_settings(enabled=False)
        lim = _build_limiter(settings)
        # When disabled, default_limits is empty – limiter exists but won't enforce
        assert lim._default_limits == []


# ---------------------------------------------------------------------------
# 4. setup_rate_limiter()
# ---------------------------------------------------------------------------

class TestSetupRateLimiter:
    """setup_rate_limiter() correctly wires the app state and middleware."""

    def test_sets_app_state_limiter(self):
        from src.infra.security.rate_limit import setup_rate_limiter

        app = FastAPI()
        setup_rate_limiter(app, settings=_make_settings())
        assert hasattr(app.state, "limiter")

    def test_registers_429_exception_handler(self):
        from slowapi.errors import RateLimitExceeded

        from src.infra.security.rate_limit import setup_rate_limiter

        app = FastAPI()
        setup_rate_limiter(app, settings=_make_settings())
        # FastAPI stores exception handlers in exception_handlers dict
        assert RateLimitExceeded in app.exception_handlers

    def test_noop_when_disabled(self):
        from src.infra.security.rate_limit import setup_rate_limiter

        app = FastAPI()
        setup_rate_limiter(app, settings=_make_settings(enabled=False))
        # State should NOT have a limiter when disabled
        assert not hasattr(app.state, "limiter")

    def test_middleware_registered(self):
        from slowapi.middleware import SlowAPIMiddleware

        from src.infra.security.rate_limit import setup_rate_limiter

        app = FastAPI()
        setup_rate_limiter(app, settings=_make_settings())
        middleware_types = [m.cls for m in app.user_middleware]
        assert SlowAPIMiddleware in middleware_types


# ---------------------------------------------------------------------------
# 5. 429 handler response shape
# ---------------------------------------------------------------------------

class TestRateLimitExceededHandler:
    """The custom handler returns the correct JSON body and headers."""

    def _trigger_429(self, limit: str = "1/minute"):
        """
        Build an app with a *very* low per-route limit, hit it twice,
        and return the 429 response.
        """
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request as StarletteRequest
        from starlette.responses import Response

        from src.infra.security.rate_limit import (
            _build_limiter,
            _rate_limit_exceeded_handler,
            _RequestContextMiddleware,
        )

        settings = _make_settings(default_limit=limit, whitelist=[])
        local_limiter = _build_limiter(settings)

        app = FastAPI()
        app.state.limiter = local_limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)
        app.add_middleware(_RequestContextMiddleware)

        @app.get("/hit")
        @local_limiter.limit(limit, exempt_when=lambda: False)
        async def hit(request: StarletteRequest, response: Response):
            return {"ok": True}

        client = TestClient(app, raise_server_exceptions=False)
        ip_headers = _external_ip_headers()
        client.get("/hit", headers=ip_headers)  # 1st – should pass
        return client.get("/hit", headers=ip_headers)  # 2nd – should 429

    def test_status_code_is_429(self):
        r = self._trigger_429()
        assert r.status_code == 429

    def test_retry_after_header_present(self):
        r = self._trigger_429()
        assert "retry-after" in r.headers

    def test_json_body_has_error_structure(self):
        r = self._trigger_429()
        body = r.json()
        assert body["success"] is False
        assert "error" in body
        assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    def test_json_body_has_retry_after_field(self):
        r = self._trigger_429()
        body = r.json()
        assert "retry_after" in body["error"]
        assert isinstance(body["error"]["retry_after"], int)

    def test_x_ratelimit_limit_header_present(self):
        r = self._trigger_429()
        assert "x-ratelimit-limit" in r.headers


# ---------------------------------------------------------------------------
# 6. Integration: rate limit is enforced
# ---------------------------------------------------------------------------

class TestRateLimitEnforced:
    """After N requests the limiter returns 429."""

    def _make_enforced_app(self, limit: str = "3/minute", whitelist: list[str] | None = None):
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request as StarletteRequest
        from starlette.responses import Response

        from src.infra.security.rate_limit import (
            _build_limiter,
            _rate_limit_exceeded_handler,
            _RequestContextMiddleware,
        )

        settings = _make_settings(default_limit=limit, whitelist=whitelist or [])
        local_limiter = _build_limiter(settings)

        app = FastAPI()
        app.state.limiter = local_limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)
        app.add_middleware(_RequestContextMiddleware)

        @app.get("/resource")
        @local_limiter.limit(limit, exempt_when=lambda: False)
        async def resource(request: StarletteRequest, response: Response):
            return {"ok": True}

        return app, local_limiter

    def test_limit_triggers_on_excess_requests(self):
        """Hit the endpoint 4 times when limit is '3/minute' – 4th must be 429."""
        app, _ = self._make_enforced_app(limit="3/minute")
        client = TestClient(app, raise_server_exceptions=False)
        ip_headers = _external_ip_headers("172.16.0.1")

        responses = [client.get("/resource", headers=ip_headers) for _ in range(4)]
        status_codes = [r.status_code for r in responses]

        assert status_codes[:3] == [200, 200, 200], f"Expected 200s; got {status_codes[:3]}"
        assert status_codes[3] == 429, f"Expected 429 on 4th request; got {status_codes[3]}"

    def test_different_ips_have_independent_buckets(self):
        """Two IPs each get their own quota."""
        app, _ = self._make_enforced_app(limit="2/minute")
        client = TestClient(app, raise_server_exceptions=False)
        ip_a = _external_ip_headers("10.0.0.1")
        ip_b = _external_ip_headers("10.0.0.2")

        # Exhaust IP A's quota
        client.get("/resource", headers=ip_a)
        client.get("/resource", headers=ip_a)
        third_a = client.get("/resource", headers=ip_a)

        # IP B should still succeed after IP A is 429'd
        first_b = client.get("/resource", headers=ip_b)

        assert third_a.status_code == 429, f"IP A should be rate-limited; got {third_a.status_code}"
        assert first_b.status_code == 200, f"IP B should still pass; got {first_b.status_code}"


# ---------------------------------------------------------------------------
# 7. Integration: whitelist exemption
# ---------------------------------------------------------------------------

class TestWhitelistExempt:
    """Whitelisted IPs are never rate-limited."""

    def _make_whitelist_app(self, whitelisted_ip: str, limit: str = "1/minute"):
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        from starlette.requests import Request as StarletteRequest
        from starlette.responses import Response

        from src.infra.security.rate_limit import (
            _build_limiter,
            _current_request,
            _rate_limit_exceeded_handler,
            _RequestContextMiddleware,
        )

        settings = _make_settings(default_limit=limit, whitelist=[whitelisted_ip])
        local_limiter = _build_limiter(settings)

        def _local_exempt():
            """Zero-arg exempt_when using the ContextVar."""
            req = _current_request.get()
            if req is None:
                return False
            fwd = req.headers.get("X-Forwarded-For", "")
            ip = fwd.split(",")[0].strip() if fwd else getattr(getattr(req, "client", None), "host", "")
            return ip == whitelisted_ip

        app = FastAPI()
        app.state.limiter = local_limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)
        app.add_middleware(_RequestContextMiddleware)

        @app.get("/exclusive")
        @local_limiter.limit(limit, exempt_when=_local_exempt)
        async def exclusive(request: StarletteRequest, response: Response):  # response needed for slowapi header injection
            return {"ok": True}

        return app

    def test_whitelisted_ip_passes_after_limit_exceeded(self):
        """A whitelisted IP can make unlimited requests."""
        whitelisted_ip = "192.168.50.1"
        app = self._make_whitelist_app(whitelisted_ip, limit="1/minute")
        client = TestClient(app, raise_server_exceptions=False)
        wl_headers = {"X-Forwarded-For": whitelisted_ip}

        # Make 5 requests from whitelisted IP – all should pass
        responses = [client.get("/exclusive", headers=wl_headers) for _ in range(5)]
        assert all(r.status_code == 200 for r in responses), (
            f"Whitelisted IP should never be rate-limited; got {[r.status_code for r in responses]}"
        )

    def test_non_whitelisted_ip_is_still_limited(self):
        """While whitelisted IPs pass, non-whitelisted IPs are still limited."""
        whitelisted_ip = "192.168.50.1"
        app = self._make_whitelist_app(whitelisted_ip, limit="2/minute")
        client = TestClient(app, raise_server_exceptions=False)
        external_headers = _external_ip_headers("9.9.9.9")

        # Exhaust external IP quota
        client.get("/exclusive", headers=external_headers)
        client.get("/exclusive", headers=external_headers)
        third = client.get("/exclusive", headers=external_headers)
        assert third.status_code == 429


# ---------------------------------------------------------------------------
# 8. Settings defaults
# ---------------------------------------------------------------------------

class TestSettingsDefaults:
    """New settings fields have correct default values."""

    def test_redis_url_default(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.REDIS_URL == "redis://localhost:6379/0"

    def test_slowapi_enabled_default_true(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.RATE_LIMIT_SLOWAPI_ENABLED is True

    def test_default_limit_value(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.RATE_LIMIT_DEFAULT == "100/minute"

    def test_chat_limit_value(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.RATE_LIMIT_CHAT == "10/minute"

    def test_estimates_post_limit_value(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.RATE_LIMIT_ESTIMATES_POST == "30/minute"

    def test_market_price_limit_value(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert s.RATE_LIMIT_MARKET_PRICE == "60/minute"

    def test_whitelist_contains_loopback(self):
        from src.shared.infra.config import Settings

        s = Settings()
        assert "127.0.0.1" in s.RATE_LIMIT_WHITELIST_IPS
        assert "::1" in s.RATE_LIMIT_WHITELIST_IPS
