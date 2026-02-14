"""
Dependency injection factories for Market Data module.

Provides FastAPI dependency functions for injecting market data
providers and services with proper configuration.
"""

from functools import lru_cache

from src.market_data.domain.providers import MarketDataProvider
from src.market_data.services.yahoo_provider import YahooMarketDataProvider
from src.market_data.infrastructure.cached_provider import (
    CachedMarketDataProvider,
    CacheConfig,
)
from src.shared.infra.config import get_settings


@lru_cache(maxsize=1)
def _get_base_provider() -> MarketDataProvider:
    """
    Get the base market data provider (singleton).
    
    Currently uses Yahoo Finance as the primary provider.
    Can be configured to use different providers based on settings.
    
    Returns:
        MarketDataProvider: Base provider instance
    """
    settings = get_settings()
    
    # TODO: Make provider selection configurable via settings
    # For now, always use Yahoo Finance
    return YahooMarketDataProvider(timeout=30)


@lru_cache(maxsize=1)
def get_market_data_provider() -> MarketDataProvider:
    """
    Get the configured market data provider with caching (singleton).
    
    Returns a CachedMarketDataProvider wrapping the base provider,
    configured with TTL and retry settings from application config.
    
    This is the recommended way to get a provider instance for
    use in FastAPI endpoints via dependency injection.
    
    Returns:
        MarketDataProvider: Cached provider with retry logic
    
    Example:
        ```python
        from fastapi import Depends
        
        @router.get("/price/{symbol}")
        async def get_price(
            symbol: str,
            provider: MarketDataProvider = Depends(get_market_data_provider),
        ):
            price = await provider.get_current_price(symbol)
            return {"price": price.close}
        ```
    """
    settings = get_settings()
    base_provider = _get_base_provider()
    
    # Configure cache and retry settings from application config
    config = CacheConfig(
        current_price_ttl=settings.CACHE_CURRENT_PRICE_TTL,
        historical_price_ttl=settings.CACHE_HISTORICAL_PRICE_TTL,
        fundamentals_ttl=settings.CACHE_FUNDAMENTALS_TTL,
        max_retries=settings.RETRY_MAX_ATTEMPTS,
        initial_backoff=settings.RETRY_INITIAL_BACKOFF,
        max_backoff=settings.RETRY_MAX_BACKOFF,
        backoff_multiplier=settings.RETRY_BACKOFF_MULTIPLIER,
        cache_maxsize=settings.CACHE_MAX_SIZE,
    )
    
    return CachedMarketDataProvider(
        underlying_provider=base_provider,
        config=config,
    )


def get_uncached_provider() -> MarketDataProvider:
    """
    Get the base provider without caching.
    
    Use this for operations where caching is not desired,
    such as real-time price updates or administrative tasks.
    
    Returns:
        MarketDataProvider: Base provider without caching
    """
    return _get_base_provider()
