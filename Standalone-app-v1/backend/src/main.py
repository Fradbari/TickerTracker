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

from src.shared.api import admin_routes
from src.estimates.api import router as estimates_router
from src.infra.logging.config import CorrelationIDMiddleware, configure_logging
from src.infra.metrics.routes import router as metrics_router

# APScheduler integration
from src.infra.scheduler import scheduler as app_scheduler
from src.infra.security.rate_limit import setup_rate_limiter
from src.market_data.api import routes as market_data_routes
from src.shared.api import health_routes
from src.shared.infra.config import get_settings
from src.shared.infra.security_middleware import setup_security_middleware

# Get application settings
settings = get_settings()

# Configure structured JSON logging BEFORE creating the app so that all
# subsequent log calls (including FastAPI startup) are formatted correctly.
configure_logging(log_level=settings.LOG_LEVEL)

# Create FastAPI application
app = FastAPI(
    title="TickerTracker Backend",
    description="Trading estimates tracking system with DDD/CQRS architecture",
    version="3.0.0",
    debug=settings.DEBUG,
    contact={"name": "TickerTracker", "email": "fra.dilecce@gmail.com"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "estimates", "description": "Gestione stime analisti"},
        {"name": "market-data", "description": "Dati di mercato Yahoo Finance"},
        {"name": "health", "description": "Health check e status"},
        {"name": "admin", "description": "Feature flags e admin"},
        {"name": "metrics", "description": "Prometheus metrics"},
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Setup slowapi rate limiter (BEFORE include_router so state is ready)
setup_rate_limiter(app)

# Setup security middleware (adds SecurityMiddleware as outermost layer)
setup_security_middleware(app)

# Add CorrelationIDMiddleware LAST so Starlette places it outermost:
# execution order → CorrelationID → Security → RequestContext → SlowAPI → app
app.add_middleware(CorrelationIDMiddleware)

# Register routers
app.include_router(health_routes.router)
app.include_router(estimates_router)
app.include_router(market_data_routes.router)
app.include_router(metrics_router)
app.include_router(admin_routes.router)

from src.shared.api.logs import router as logs_router
app.include_router(logs_router)

if settings.ENVIRONMENT in ['local', 'test']:
    from src.shared.api import test_routes
    app.include_router(test_routes.router)  # ✅ [3.6] GET /metrics — Prometheus scrape endpoint

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


from sqlalchemy.exc import TimeoutError as SATimeoutError


@app.exception_handler(SATimeoutError)
async def db_timeout_exception_handler(request: Request, exc: SATimeoutError) -> JSONResponse:
    """Handle database pool exhaustion / timeout."""
    return JSONResponse(
        status_code=503,
        content={"status": 503, "code": "DB_UNAVAILABLE", "detail": "Service temporally unavailable due to high load"},
    )

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
