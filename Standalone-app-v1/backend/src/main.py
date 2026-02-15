"""
TickerTracker Backend - FastAPI Application Entry Point

Configures:
- FastAPI application
- Security middleware (headers, CORS, rate limiting)
- Health check routes
- All bounded context routers
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.api import health_routes
from src.estimates.api import router as estimates_router
from src.market_data.api import routes as market_data_routes
from src.shared.infra.config import get_settings

from src.shared.infra.security_middleware import setup_security_middleware

# APScheduler integration
from src.infra.scheduler import scheduler as app_scheduler

# Get application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="TickerTracker Backend",
    description="Trading estimates tracking system with DDD/CQRS architecture",
    version="3.0.0",
    debug=settings.DEBUG,
)

# Setup security middleware
setup_security_middleware(app)

# Register routers
app.include_router(health_routes.router)
app.include_router(estimates_router)
app.include_router(market_data_routes.router)

# TODO: Register additional bounded context routers
# - sync
# - analytics


# APScheduler startup/shutdown hooks
@app.on_event("startup")
async def start_scheduler_event():
    app_scheduler.start_scheduler()

@app.on_event("shutdown")
async def shutdown_scheduler_event():
    app_scheduler.shutdown_scheduler()


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint - API status."""
    return {
        "status": "running",
        "application": "TickerTracker Backend",
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions."""
    if settings.DEBUG:
        raise exc

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
