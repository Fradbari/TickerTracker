"""
TickerTracker Backend - FastAPI Application Entry Point

Configures:
- FastAPI application
- Security middleware (headers, CORS, rate limiting)
- Health check routes
- All bounded context routers
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.shared.api import health_routes
from src.shared.infra.config import get_settings
from src.shared.infra.security_middleware import setup_security_middleware

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

# TODO: Register bounded context routers
# - estimates
# - market_data
# - sync
# - analytics


@app.get("/", tags=["root"])
async def root():
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
async def global_exception_handler(request, exc):
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
