"""
Health check endpoints for application monitoring and Kubernetes probes (Task 3.7).

Endpoints
---------
GET /health       Full system health — aggregates all component checks.
                  HTTP 200 even if DEGRADED; HTTP 503 if UNHEALTHY.

GET /health/ready Kubernetes readiness probe — verifies DB only.
                  HTTP 200 if database is HEALTHY; HTTP 503 otherwise.

GET /health/live  Kubernetes liveness probe — always HTTP 200.
                  No external check: if this responds, the process is alive.

Architecture
------------
Route handlers are thin: they delegate all check logic to
``src.infra.health.health_service.HealthService``.  This keeps the router
import-safe (no DB imports at module level) and the service fully unit-testable
without an HTTP layer.
"""

import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.infra.health.health_service import (
    HealthService,
    SystemHealth,
)

# ---------------------------------------------------------------------------
# Router — MUST stay here with this prefix; already registered in main.py.
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/health", tags=["health"])

# Capture process start time for the /health/live uptime field.
_process_start: float = time.monotonic()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _system_health_to_dict(health: SystemHealth) -> dict:
    """Convert SystemHealth (dataclass) to a plain JSON-serialisable dict."""
    return {
        "status": health.status,
        "version": health.version,
        "uptime_seconds": health.uptime_seconds,
        "ready": health.is_ready,
        "components": [
            {
                "name": c.name,
                "status": c.status,
                "latency_ms": c.latency_ms,
                "message": c.message,
            }
            for c in health.components
        ],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("")
async def health_check() -> JSONResponse:
    """
    Full system health check.

    Runs all component checks IN PARALLEL (database, Redis, Yahoo Finance,
    Google Drive) and returns the aggregated result.

    HTTP 200 if status is HEALTHY or DEGRADED (system is functional).
    HTTP 503 if status is UNHEALTHY (critical dependency is DOWN).

    Exempt from API key authentication (see config.API_KEY_EXEMPT_PATHS).
    """
    health = await HealthService().check_all()
    http_status = 503 if health.status == "UNHEALTHY" else 200
    return JSONResponse(content=_system_health_to_dict(health), status_code=http_status)


@router.get("/ready")
async def ready_check() -> JSONResponse:
    """
    Kubernetes readiness probe.

    Verifies only the database (the single critical dependency).
    HTTP 200 if HEALTHY; HTTP 503 otherwise.
    """
    db_health = await HealthService().check_database()
    is_ready = db_health.status == "HEALTHY"
    payload: dict = {
        "ready": is_ready,
        "database": db_health.status,
        "latency_ms": db_health.latency_ms,
    }
    if db_health.message:
        payload["message"] = db_health.message
    return JSONResponse(content=payload, status_code=200 if is_ready else 503)


@router.get("/live")
async def liveness_check() -> JSONResponse:
    """
    Kubernetes liveness probe.

    No external checks — if this endpoint responds the process is alive.
    Always returns HTTP 200.
    """
    uptime = round(time.monotonic() - _process_start, 2)
    return JSONResponse(
        content={"alive": True, "uptime_seconds": uptime},
        status_code=200,
    )
