"""
Structured Logging with Correlation ID for TickerTracker backend (Task 3.5).

Provides:
- ``correlation_id`` ContextVar — propagated through the request lifecycle.
- ``add_correlation_id`` processor — injects it into every structlog event.
- ``configure_logging()`` — one-shot idempotent structlog setup with JSON output.
- ``CorrelationIDMiddleware`` — Starlette middleware that reads/generates the ID
  and adds it to the response ``X-Correlation-ID`` header.

Usage in main.py
----------------
::

    from src.infra.logging.config import configure_logging, CorrelationIDMiddleware

    configure_logging(log_level=get_settings().LOG_LEVEL)  # before creating app

    app = FastAPI(...)
    ...
    # Add LAST so it is outermost (executed first for every request)
    app.add_middleware(CorrelationIDMiddleware)

Header convention
-----------------
- ``X-Correlation-ID``  — managed by this middleware (Task 3.5).
- ``X-Request-ID``      — managed by SecurityMiddleware (Task 3.1), distinct.

Environment variable
--------------------
``LOG_LEVEL`` in ``.env`` controls the log verbosity (DEBUG / INFO / WARNING /
ERROR / CRITICAL).  Defaults to ``INFO`` when not supplied.
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ---------------------------------------------------------------------------
# ContextVar for correlation ID
# ---------------------------------------------------------------------------

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

# ---------------------------------------------------------------------------
# Custom structlog processor
# ---------------------------------------------------------------------------


def add_correlation_id(logger, method, event_dict):  # noqa: ANN001
    """Structlog processor: injects correlation_id from ContextVar into event_dict."""
    cid = correlation_id.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


# ---------------------------------------------------------------------------
# Configure structlog  (idempotent)
# ---------------------------------------------------------------------------

_configured: bool = False


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structlog for JSON structured logging.

    Idempotent — calling this function a second time is a no-op, so it is
    safe to call from tests, application startup, and library code.

    Parameters
    ----------
    log_level:
        A stdlib-compatible level name (``"DEBUG"``, ``"INFO"``, …).
        Defaults to ``"INFO"``.
    """
    global _configured  # noqa: PLW0603
    if _configured:
        return

    log_level_int: int = getattr(logging, log_level.upper(), logging.INFO)

    # Route stdlib loggers (uvicorn, sqlalchemy, …) through structlog so they
    # also emit JSON with the same processor chain.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level_int,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_correlation_id,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _configured = True


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that manages the ``X-Correlation-ID`` header.

    Behaviour
    ---------
    1. Reads ``X-Correlation-ID`` from the incoming request; falls back to a
       freshly generated UUID4 when the header is absent.
    2. Stores the ID in the ``correlation_id`` ContextVar so that every
       structlog call within the request lifecycle includes it automatically.
    3. Adds ``X-Correlation-ID`` to the response headers.
    4. Resets the ContextVar after the request to avoid leaking state.

    Registration order
    ------------------
    Add this middleware **last** (after all other ``add_middleware`` calls) so
    that Starlette places it outermost in the chain — meaning it executes first
    for every incoming request.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        cid: str = request.headers.get("X-Correlation-ID") or str(uuid4())
        token = correlation_id.set(cid)
        try:
            response: Response = await call_next(request)
        finally:
            correlation_id.reset(token)
        response.headers["X-Correlation-ID"] = cid
        return response
