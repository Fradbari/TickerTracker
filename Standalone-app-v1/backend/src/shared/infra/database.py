"""
Database configuration and session management for TickerTracker backend.

This module provides:
- Async SQLAlchemy engine configuration
- Base declarative class for all models
- Session factory for database operations
- FastAPI dependency for database sessions
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from src.shared.infra.config import get_settings

# Create declarative base for all models
Base = declarative_base()

# Get settings instance
settings = get_settings()

# Create async engine with configuration
# Pool size: 5 for development, 20 for production
# Echo: True in development for SQL logging
engine = create_async_engine(
    settings.DATABASE_URL.get_secret_value(),
    echo=settings.DEBUG,
    pool_size=5 if settings.ENVIRONMENT == "local" else 20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


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
