"""
TickerTracker Backend - FastAPI Application Entry Point

Configures:
- FastAPI application with DDD/CQRS architecture
- Security middleware (headers, CORS, rate limiting) in specific order
- Health check routes (both at root and /api for compatibility)
- All bounded context routers (estimates, market-data, sync, admin, metrics, etc.)
- Background services (APScheduler for jobs, price update loop)
- Exception handling for database timeouts and generic errors
- Lifespan events for startup/shutdown tasks (candle backfill, background loops)

The application follows Clean Architecture principles with strict layer separation:
API → Services → Repositories → Domain
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
from src.sync.api.routes import router as sync_router
from src.shared.api import health_routes
from src.shared.infra.config import get_settings
from src.shared.infra.security_middleware import setup_security_middleware
import asyncio
from contextlib import asynccontextmanager
from src.shared import background_tasks
from src.market_data import candle_service
from src.shared.infra.database import AsyncSessionLocal

# Get application settings
settings = get_settings()

# Configure structured JSON logging BEFORE creating the app so that all
# subsequent log calls (including FastAPI startup) are formatted correctly.
# This ensures consistent logging format across the entire application lifecycle.
configure_logging(log_level=settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown tasks for background services.
    """
    # TASK 4 (Prima): Execute candle backfill on startup to ensure initial market data
    # This populates the database with historical candles for immediate charting
    await candle_service.backfill_candles_on_startup()

    # TASK 3B (Dopo): Start asynchronous price update loop
    # This loop periodically fetches latest market data for all tracked tickers
    # We store the task reference to cancel it cleanly on shutdown
    loop_task = asyncio.create_task(background_tasks.start_price_loop({"db_session": AsyncSessionLocal}))
    yield
    # Cancel the background price loop when application shuts down
    loop_task.cancel()

# Create FastAPI application with metadata for OpenAPI/Swagger documentation
app = FastAPI(
    title="TickerTracker Backend",
    description="Trading estimates tracking system with DDD/CQRS architecture",
    version="3.0.0",
    debug=settings.DEBUG,
    contact={"name": "TickerTracker", "email": "fra.dilecce@gmail.com"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
    openapi_tags=[
        {"name": "estimates", "description": "Gestione stime analisti"},
        {"name": "market-data", "description": "Dati di mercato Yahoo Finance"},
        {"name": "health", "description": "Health check e status"},
        {"name": "admin", "description": "Feature flags e admin"},
        {"name": "metrics", "description": "Prometheus metrics"},
    ],
    # Swagger UI configuration: hide schemas by default for cleaner interface
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Setup slowapi rate limiter BEFORE including routers
# This ensures the rate limiter state is initialized before any route definitions
setup_rate_limiter(app)

# Setup security middleware (adds SecurityMiddleware as outermost layer)
# This middleware handles security headers, CORS, and other protection measures
setup_security_middleware(app)

# Add CorrelationIDMiddleware LAST so Starlette places it outermost in the middleware stack
# Execution order of middleware (from outer to inner):
# 1. CorrelationIDMiddleware (adds request ID for tracing)
# 2. SecurityMiddleware (adds security headers)
# 3. RequestContext (FastAPI's built-in)
# 4. SlowAPI (rate limiting)
# 5. Application routes
app.add_middleware(CorrelationIDMiddleware)

# Register routers for each bounded context
# Health routes are registered twice: at root (for Docker/K8s probes) and at /api (for consistency)
app.include_router(health_routes.router)           # Root level: /health
app.include_router(health_routes.router, prefix="/api")  # API level: /api/health (bypasses nginx intercept in prod)

# Core business logic routers
app.include_router(estimates_router)               # /estimates
app.include_router(market_data_routes.router)      # /market-data
app.include_router(sync_router, prefix="/api")     # /api/sync (Google Drive synchronization)
app.include_router(metrics_router)                 # /metrics (Prometheus endpoint)
app.include_router(admin_routes.router)            # /admin (feature flags and admin endpoints)

# Shared infrastructure routers
from src.shared.api.logs import router as logs_router
from src.shared.router import router as shared_tasks_router
app.include_router(logs_router)                    # /logs (internal logging endpoint)
app.include_router(shared_tasks_router)            # /tasks (background task management)

# Test routes (only in local/test environments)
if settings.ENVIRONMENT in ['local', 'test']:
    from src.shared.api import test_routes
    app.include_router(test_routes.router)         # /test (includes Prometheus scrape endpoint at /metrics)

# TODO: Register additional bounded context routers
# - analytics (Phase 2 feature for advanced reporting and insights)

# APScheduler startup/shutdown hooks
# These events start and stop the background job scheduler
@app.on_event("startup")
async def start_scheduler_event():
    app_scheduler.start_scheduler()

@app.on_event("shutdown")
async def shutdown_scheduler_event():
    app_scheduler.shutdown_scheduler()


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint - returns basic API status and navigation links."""
    return {
        "status": "running",
        "application": "TickerTracker Backend",
        "version": "3.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
    }


# Import placed here to avoid circular import issues with SQLAlchemy
from sqlalchemy.exc import TimeoutError as SATimeoutError


@app.exception_handler(SATimeoutError)
async def db_timeout_exception_handler(request: Request, exc: SATimeoutError) -> JSONResponse:
    """Handle database pool exhaustion / timeout.

    Returns 503 Service Unavailable when the database connection pool is exhausted,
    indicating temporary unavailability due to high load.
    """
    return JSONResponse(
        status_code=503,
        content={"status": 503, "code": "DB_UNAVAILABLE", "detail": "Service temporally unavailable due to high load"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.

    In debug mode, re-raises the exception to provide detailed tracebacks.
    In production, returns a generic 500 error to avoid leaking internal details.
    """
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