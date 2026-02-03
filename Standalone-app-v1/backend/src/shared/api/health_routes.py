"""
Health check endpoints for application monitoring and Docker health probes.

Endpoints:
- GET /health - Basic health check (always returns 200 OK)
- GET /health/ready - Readiness check (all dependencies OK)
"""

from typing import Any
from uuid import uuid4

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.schemas.api_response import ApiResponse, success_response

# Health check router
router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=ApiResponse[dict[str, str]])
async def health_check() -> ApiResponse[dict[str, str]]:
    """
    Basic health check endpoint.

    Always returns 200 OK if the application is running.
    Suitable for Docker HEALTHCHECK or load balancer probes.

    Returns:
        ApiResponse: {success: true, data: {status: "ok"}}
    """
    return success_response(data={"status": "ok"}, trace_id=str(uuid4()))


@router.get("/ready", response_model=ApiResponse[dict[str, Any]])
async def ready_check() -> ApiResponse[dict[str, Any]]:
    """
    Readiness check endpoint.

    Returns 200 OK when the application is ready to handle requests.
    Should check all critical dependencies (database, cache, etc.).

    Future: Add checks for cache, external APIs, etc.

    Returns:
        ApiResponse: {success: true, data: {status: "ready", checks: {...}}}
    """
    # TODO: Check database connection
    # TODO: Check Redis connection
    # TODO: Check external API connectivity

    return success_response(
        data={
            "status": "ready",
            "checks": {
                "database": "pending",
                "cache": "pending",
                "external_apis": "pending",
            },
        },
        trace_id=str(uuid4()),
    )


# TODO: Implement database check when database is configured
# For now, this is a placeholder that shows the pattern
async def get_db_session() -> AsyncSession:
    """Dependency to get database session.

    TODO: Implement when database is configured in Phase 2.
    """
    # This will be implemented in Phase 2 when database is configured
    raise NotImplementedError("Database not configured yet")


# Uncomment this once database is configured in Phase 2
# @router.get("/db", response_model=ApiResponse)
# async def db_health_check(db: AsyncSession = Depends(get_db_session)) -> ApiResponse:
#     """
#     Database connectivity check.
#
#     Executes a simple SELECT 1 query to verify database is reachable.
#     Returns 500 if database is unavailable.
#
#     Returns:
#         ApiResponse: {status: "ok", database: "connected"}
#
#     Raises:
#         HTTPException: 500 if database is unreachable
#     """
#     try:
#         result = await db.execute(text("SELECT 1"))
#         result.fetchone()
#         return create_response(data={"status": "ok", "database": "connected"})
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Database connection failed: {str(e)}"
#         )
