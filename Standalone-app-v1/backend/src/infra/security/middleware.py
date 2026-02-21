"""
SecurityMiddleware – infra/security layer (Task 3.1).

Responsibilities (single pass, <1 ms overhead):
1. API-key validation  – optional, controlled by Settings.ENABLE_API_KEY_AUTH
   • Checks X-API-Key header against Settings.API_KEY
   • Configurable exempt paths (health, docs, openapi)
   • Returns HTTP 401 immediately on missing/invalid key
2. Security response headers
   • X-Content-Type-Options: nosniff
   • X-Frame-Options: DENY
   • X-XSS-Protection: 1; mode=block
   • Strict-Transport-Security (HTTPS requests only)
   • Content-Security-Policy (configurable, disable with empty string)
3. Structured request logging (structlog)
   • Fields: method, path, status_code, duration_ms, client_ip, request_id
   • Controlled by Settings.REQUEST_LOG_ENABLED

Registration:
    Call ``register_security_middleware(app)`` from your application factory
    **after** adding other middlewares (Starlette executes in reverse order).

Examples:
    >>> from src.infra.security.middleware import register_security_middleware
    >>> register_security_middleware(app)
"""

from __future__ import annotations

import secrets
import time
import logging
from collections.abc import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from fastapi import FastAPI

try:
    import structlog

    _logger = structlog.get_logger(__name__)
    _USE_STRUCTLOG = True
except ImportError:  # pragma: no cover – structlog is in requirements.txt
    _logger = logging.getLogger(__name__)  # type: ignore[assignment]
    _USE_STRUCTLOG = False


def _get_settings():
    """Lazy import to avoid circular imports at module load time."""
    from src.shared.infra.config import get_settings  # noqa: PLC0415

    return get_settings()


# ---------------------------------------------------------------------------
# Security headers helpers
# ---------------------------------------------------------------------------

_STATIC_HEADERS: list[tuple[str, str]] = [
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("X-XSS-Protection", "1; mode=block"),
]

_HSTS_VALUE = "max-age=31536000; includeSubDomains; preload"


def _apply_security_headers(response: Response, *, is_https: bool, csp_policy: str) -> None:
    """Mutate *response* in-place: add security headers."""
    for header, value in _STATIC_HEADERS:
        response.headers[header] = value

    if is_https:
        response.headers["Strict-Transport-Security"] = _HSTS_VALUE

    if csp_policy:
        response.headers["Content-Security-Policy"] = csp_policy


# ---------------------------------------------------------------------------
# Client IP extraction
# ---------------------------------------------------------------------------

def _client_ip(request: Request) -> str:
    """Return best-guess client IP (handles reverse-proxy X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


# ---------------------------------------------------------------------------
# SecurityMiddleware
# ---------------------------------------------------------------------------

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Centralised security middleware for the TickerTracker backend.

    Reads configuration once at instantiation from ``get_settings()`` so that
    overhead per request is limited to memory lookups, not I/O or parsing.

    Args:
        app:     The ASGI app to wrap.
        settings: Injected settings (defaults to ``get_settings()``).  Pass an
                  explicit instance in tests to avoid cache / .env pollution.
    """

    def __init__(self, app, settings=None) -> None:  # noqa: ANN001
        super().__init__(app)
        cfg = settings or _get_settings()

        self._api_key_enabled: bool = cfg.ENABLE_API_KEY_AUTH
        self._api_key: str = (
            cfg.API_KEY.get_secret_value() if self._api_key_enabled else ""
        )
        self._exempt_paths: frozenset[str] = frozenset(cfg.API_KEY_EXEMPT_PATHS)
        self._csp_policy: str = cfg.CSP_POLICY
        self._log_requests: bool = cfg.REQUEST_LOG_ENABLED

    # ------------------------------------------------------------------
    # Core dispatch
    # ------------------------------------------------------------------

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start = time.perf_counter()
        request_id = request.headers.get("X-Request-ID") or secrets.token_hex(8)

        # 1. API-key validation (early return, before any route processing)
        if self._api_key_enabled and not self._is_exempt(request):
            auth_error = self._validate_api_key(request)
            if auth_error is not None:
                _apply_security_headers(
                    auth_error,
                    is_https=request.url.scheme == "https",
                    csp_policy=self._csp_policy,
                )
                self._log(
                    "request",
                    method=request.method,
                    path=request.url.path,
                    status_code=auth_error.status_code,
                    duration_ms=round((time.perf_counter() - start) * 1000, 2),
                    client_ip=_client_ip(request),
                    request_id=request_id,
                    auth_error=True,
                )
                return auth_error

        # 2. Process request through the rest of the middleware stack / routes
        response: Response = await call_next(request)

        # 3. Attach security headers to the actual response
        _apply_security_headers(
            response,
            is_https=request.url.scheme == "https",
            csp_policy=self._csp_policy,
        )

        # 4. Structured request log
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        self._log(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=_client_ip(request),
            request_id=request_id,
        )

        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _is_exempt(self, request: Request) -> bool:
        """Return True if the request path is exempt from API-key validation."""
        path = request.url.path
        # Exact match
        if path in self._exempt_paths:
            return True
        # Prefix match (e.g. /health covers /health/ready etc.)
        return any(path.startswith(exempt) for exempt in self._exempt_paths if exempt.endswith("/"))

    def _validate_api_key(self, request: Request) -> JSONResponse | None:
        """
        Return a ``JSONResponse(401)`` if the API key is missing or wrong,
        ``None`` if validation passes.

        Uses ``secrets.compare_digest`` to prevent timing-based attacks.
        """
        provided = request.headers.get("X-API-Key", "")
        if not provided:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing X-API-Key header"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
        if not secrets.compare_digest(provided, self._api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key"},
                headers={"WWW-Authenticate": "ApiKey"},
            )
        return None

    def _log(self, event: str, **fields) -> None:  # noqa: ANN003
        """Emit a structured log record if request logging is enabled."""
        if not self._log_requests:
            return
        if _USE_STRUCTLOG:
            _logger.info(event, **fields)
        else:  # pragma: no cover
            _logger.info(event, extra=fields)


# ---------------------------------------------------------------------------
# Registration helper
# ---------------------------------------------------------------------------

def register_security_middleware(app: FastAPI, settings=None) -> None:  # noqa: ANN001
    """
    Register ``SecurityMiddleware`` on *app*.

    Call this **after** other ``add_middleware`` calls (Starlette wraps in
    reverse insertion order, so this middleware will execute first).

    Args:
        app:      FastAPI application instance.
        settings: Optional Settings override (useful in tests).
    """
    app.add_middleware(SecurityMiddleware, settings=settings)
