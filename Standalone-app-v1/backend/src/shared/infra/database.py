"""
Database configuration and session management — Task 3.10 (connection pooling).

This module provides:
- Async SQLAlchemy engine with optimised **QueuePool** settings (configurable via Settings)
- Base declarative class for all models
- Session factory for database operations
- FastAPI dependency for database sessions
- ``get_pool_status()`` for diagnostics and Prometheus metrics

Note: ``create_async_engine`` automatically uses ``AsyncAdaptedQueuePool``
(a QueuePool wrapper).  Pool knobs (size, overflow, recycle …) are forwarded
directly — there is no need to set ``poolclass`` explicitly.
"""

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.shared.infra.config import get_settings

_logger = structlog.get_logger(__name__)

# Create declarative base for all models
Base = declarative_base()

# Get settings instance
settings = get_settings()

# ---------------------------------------------------------------------------
# Async engine with QueuePool — all knobs driven by Settings (Task 3.10)
# Note: create_async_engine uses AsyncAdaptedQueuePool by default;
#       pool_* kwargs are forwarded to the underlying QueuePool.
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL.get_secret_value(),
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)

_logger.info(
    "database_pool_configured",
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    environment=settings.ENVIRONMENT,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# Pool diagnostics (Task 3.10)
# ---------------------------------------------------------------------------

def get_pool_status() -> dict:
    """
    Return current connection-pool status for metrics and diagnostics.

    Safe to call at any time — no DB connection is required.
    Works with both ``QueuePool`` and ``AsyncAdaptedQueuePool``.

    Returns:
        dict with keys: pool_size, checked_in, checked_out, overflow, invalid.
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": getattr(pool, "invalid", lambda: 0)(),
    }


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        AsyncSession: Database session for request handling

    Example:
        ```python
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
