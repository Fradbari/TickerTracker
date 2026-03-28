"""
Rate Limiting Module – infra/security layer (Task 3.2).

Uses `slowapi` (wraps the `limits` library) with:
- **Redis storage** for cross-instance sharing (in-memory fallback when Redis is
  unreachable at startup).
- **Default limit**: 100 req/minute per IP (configurable via RATE_LIMIT_DEFAULT).
- **Per-endpoint overrides** via the `@limiter.limit(...)` decorator:
    - /api/chat:               10  req/minute  (RATE_LIMIT_CHAT)
    - /api/estimates  POST:    30  req/minute  (RATE_LIMIT_ESTIMATES_POST)
    - /api/market/price/:      60  req/minute  (RATE_LIMIT_MARKET_PRICE)
- **Whitelist**: IPs in ``RATE_LIMIT_WHITELIST_IPS`` are exempt from every limit
  via the ``exempt_when`` parameter supported by slowapi.
- **HTTP 429** responses include ``Retry-After`` and ``X-RateLimit-*`` headers.

Registration (called in ``main.py``):
    >>> from src.infra.security.rate_limit import setup_rate_limiter
    >>> setup_rate_limiter(app)

Decorating route handlers:
    >>> from src.infra.security.rate_limit import limiter, is_whitelisted
    >>>
    >>> @router.post("/resource")
    >>> @limiter.limit("30/minute", exempt_when=is_whitelisted)
    >>> async def create_resource(request: Request, ...):
    ...     ...

Note:
    Every decorated route function **must** include ``request: Request`` as a
    parameter so that slowapi can access the incoming request object.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from contextvars import ContextVar

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

try:
    import structlog

    _logger = structlog.get_logger(__name__)
    _USE_STRUCTLOG = True
except ImportError:  # pragma: no cover
    _logger = logging.getLogger(__name__)  # type: ignore[assignment]
    _USE_STRUCTLOG = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# ContextVar that holds the current Request for every active asyncio task.
# Set by _RequestContextMiddleware so that is_whitelisted() (which slowapi
# calls with ZERO arguments) can still read the incoming request.
_current_request: ContextVar[Request | None] = ContextVar("_current_request", default=None)

def _get_settings():
    """Lazy import to avoid circular imports at module load time."""
    from src.shared.infra.config import get_settings  # noqa: PLC0415

    return get_settings()


def _client_ip(request: Request) -> str:
    """Extract client IP, honouring X-Forwarded-For proxy chains."""
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


# ---------------------------------------------------------------------------
# Limiter factory
# ---------------------------------------------------------------------------

def _build_limiter(settings=None) -> Limiter:
    """
    Create a ``Limiter`` instance.

    Tries Redis first; falls back to in-memory if Redis is unreachable.
    The module-level ``limiter`` is initialised at import time using the
    cached Settings singleton.  Tests may call this directly with a mock
    Settings to get an isolated limiter.
    """
    cfg = settings or _get_settings()
    storage_uri: str = cfg.REDIS_URL

    # Probe Redis connectivity; downgrade to memory on failure so the app
    # always starts even without Redis.
    try:
        import redis as _redis_pkg  # noqa: PLC0415

        probe = _redis_pkg.from_url(storage_uri, socket_connect_timeout=1)
        probe.ping()
        if _USE_STRUCTLOG:
            _logger.info("rate_limiter.storage", backend="redis", uri=storage_uri)
        else:
            _logger.info("rate_limiter: using Redis storage at %s", storage_uri)
    except Exception as exc:  # redis not available
        storage_uri = "memory://"
        if _USE_STRUCTLOG:
            _logger.warning(
                "rate_limiter.fallback_to_memory",
                reason=str(exc),
            )
        else:
            _logger.warning("rate_limiter: Redis unavailable (%s) – using memory", exc)

    default_limits: list[str] = (
        [cfg.RATE_LIMIT_DEFAULT] if cfg.RATE_LIMIT_SLOWAPI_ENABLED else []
    )

    return Limiter(
        key_func=_client_ip,
        default_limits=default_limits,
        storage_uri=storage_uri,
        headers_enabled=True,  # exposes X-RateLimit-* headers
    )


# ---------------------------------------------------------------------------
# Module-level singleton
# Imported by route modules to apply @limiter.limit() decorators.
# ---------------------------------------------------------------------------

limiter: Limiter = _build_limiter()


# ---------------------------------------------------------------------------
# Whitelist helper
# ---------------------------------------------------------------------------

def is_whitelisted() -> bool:
    """
    Return *True* if the current request should be exempt from rate limiting.

    **Zero-argument callable** – required by slowapi's ``exempt_when``
    parameter (slowapi calls it as ``exempt_when()`` with no arguments).

    The request object is retrieved from the ``_current_request`` ContextVar
    which is populated per-request by ``_RequestContextMiddleware``.  This
    must be registered in the middleware stack for the whitelist to work.

    IPs are read from ``RATE_LIMIT_WHITELIST_IPS`` at call-time so that
    environment variable changes take effect after a restart without
    rebuilding the limiter.

    Decorator usage::

        @limiter.limit("30/minute", exempt_when=is_whitelisted)
        async def create_estimate(request: Request, ...): ...
    """
    request = _current_request.get()
    if request is None:
        return False
    cfg = _get_settings()
    whitelist: frozenset[str] = frozenset(cfg.RATE_LIMIT_WHITELIST_IPS)
    return _client_ip(request) in whitelist


class _RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware that stores the current ``Request`` in a
    ``ContextVar`` so that ``is_whitelisted()`` can read it without
    receiving the request as a parameter (required by slowapi).

    It must run BEFORE ``SlowAPIMiddleware`` requests arrive, i.e. it must
    be registered AFTER ``SlowAPIMiddleware`` (Starlette processes in reverse
    registration order).
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        token = _current_request.set(request)
        try:
            return await call_next(request)
        finally:
            _current_request.reset(token)


# ---------------------------------------------------------------------------
# 429 exception handler
# ---------------------------------------------------------------------------

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Return HTTP 429 with ``Retry-After`` and ``X-RateLimit-*`` headers.

    slowapi raises ``RateLimitExceeded`` (a subclass of ``HTTPException``)
    when a limit is hit.  This handler converts it to the project's standard
    ``ApiResponse``-like JSON shape and injects all headers.

    The ``Retry-After`` value defaults to 60 (worst-case for per-minute
    windows).  slowapi's ``headers_enabled=True`` adds a more precise
    ``X-RateLimit-Reset`` (Unix timestamp) for clients that need it.
    """
    # Best-effort retry_after: use exc attribute when available, else 60 s.
    retry_after: int = int(getattr(exc, "retry_after", 60))
    limit_detail: str = str(exc.detail) if exc.detail else "rate limit exceeded"

    if _USE_STRUCTLOG:
        _logger.warning(
            "rate_limit.exceeded",
            path=request.url.path,
            method=request.method,
            client_ip=_client_ip(request),
            limit=limit_detail,
            retry_after=retry_after,
        )
    else:
        _logger.warning(
            "rate_limit.exceeded path=%s method=%s ip=%s retry_after=%s",
            request.url.path,
            request.method,
            _client_ip(request),
            retry_after,
        )

    response = JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    f"Rate limit exceeded: {limit_detail}. "
                    f"Retry after {retry_after} seconds."
                ),
                "retry_after": retry_after,
            },
            "data": None,
            "trace_id": None,
        },
    )
    response.headers["Retry-After"] = str(retry_after)
    response.headers["X-RateLimit-Limit"] = limit_detail

    # Inject slowapi's X-RateLimit-Remaining / X-RateLimit-Reset headers when
    # the view_rate_limit state is available (set by SlowAPIMiddleware).
    try:
        vrl = getattr(request.state, "view_rate_limit", None)
        if vrl is not None and hasattr(request.app.state, "limiter"):
            response = request.app.state.limiter._inject_headers(response, vrl)
    except Exception:  # pragma: no cover – defensive
        pass

    return response


# ---------------------------------------------------------------------------
# Application wiring
# ---------------------------------------------------------------------------

def setup_rate_limiter(app: FastAPI, settings=None) -> None:
    """
    Register the rate limiter with a FastAPI application.

    This must be called **before** ``app.include_router(...)`` so that
    ``app.state.limiter`` exists when route handlers are loaded.

    Call sequence in ``main.py``::

        setup_rate_limiter(app)      # 1st – sets up state + middleware
        app.include_router(...)      # 2nd – routes see app.state.limiter

    When ``settings.RATE_LIMIT_SLOWAPI_ENABLED`` is *False* this function
    is a no-op (useful in local single-user development).

    Args:
        app: The FastAPI application instance.
        settings: Optional Settings override (used by integration tests to
                  inject a mock Settings without affecting the global singleton).
    """
    global limiter  # noqa: PLW0603

    cfg = settings or _get_settings()

    if not cfg.RATE_LIMIT_SLOWAPI_ENABLED:
        if _USE_STRUCTLOG:
            _logger.info("rate_limiter.disabled", reason="RATE_LIMIT_SLOWAPI_ENABLED=False")
        return

    # Allow tests to inject an isolated limiter by passing custom settings.
    if settings is not None:
        limiter = _build_limiter(settings)

    # Attach limiter to app state (required by SlowAPIMiddleware).
    app.state.limiter = limiter

    # Register 429 handler BEFORE middleware so FastAPI sees it.
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # SlowAPIMiddleware intercepts every request and checks rate limits.
    # _RequestContextMiddleware must be added AFTER SlowAPIMiddleware so it
    # executes FIRST (Starlette reverses middleware order), populating the
    # ContextVar before slowapi's exempt_when() is evaluated.
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(_RequestContextMiddleware)

    if _USE_STRUCTLOG:
        _logger.info(
            "rate_limiter.registered",
            default_limit=cfg.RATE_LIMIT_DEFAULT,
            whitelist_ips=cfg.RATE_LIMIT_WHITELIST_IPS,
            storage=(
                "redis" if not cfg.REDIS_URL.startswith("memory") else "memory"
            ),
        )
