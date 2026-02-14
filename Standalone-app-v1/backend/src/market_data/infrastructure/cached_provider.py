"""
Cached Market Data Provider - Decorator with TTL caching and retry logic.

Wraps any MarketDataProvider to add:
- TTL-based caching to reduce external API calls
- Retry with exponential backoff on errors
- Fallback to stale cached data when API unavailable
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import date as DateType
from typing import List, Optional
from decimal import Decimal

from src.market_data.domain.providers import (
    MarketDataProvider,
    PriceData,
    FundamentalsData,
    MarketDataProviderError,
    RateLimitExceededError,
)
from src.infra.cache import MemoryCache, CacheKeyBuilder

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """
    Configuration for cached provider behavior.
    
    Attributes:
        current_price_ttl: TTL for current price data (seconds)
        historical_price_ttl: TTL for historical data (seconds)
        fundamentals_ttl: TTL for fundamentals data (seconds)
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff delay in seconds
        max_backoff: Maximum backoff delay in seconds
        backoff_multiplier: Exponential backoff multiplier
        cache_maxsize: Maximum cache size (number of items)
    """
    current_price_ttl: int = 60  # 60 seconds for current prices
    historical_price_ttl: int = 3600  # 1 hour for historical data
    fundamentals_ttl: int = 86400  # 24 hours for fundamentals
    max_retries: int = 3
    initial_backoff: float = 0.5  # 500ms
    max_backoff: float = 8.0  # 8 seconds
    backoff_multiplier: float = 2.0
    cache_maxsize: int = 1000


class CachedMarketDataProvider(MarketDataProvider):
    """
    Market data provider decorator with caching and retry logic.
    
    Wraps an underlying provider (e.g., YahooMarketDataProvider) to add:
    
    1. **TTL-based caching**: Reduces external API calls
       - Current prices: 60s TTL
       - Historical data: 1h TTL  
       - Fundamentals: 24h TTL
    
    2. **Exponential backoff retry**: Handles transient errors
       - Retries on timeouts and rate limits
       - Exponential delay: 0.5s, 1s, 2s, 4s, 8s...
       - Max 3 retries by default
    
    3. **Stale data fallback**: Graceful degradation
       - If all retries fail, returns stale cached data if available
       - Marks data with is_stale=True
       - Prevents hard failures when API unavailable
    
    Example:
        >>> base_provider = YahooMarketDataProvider()
        >>> config = CacheConfig(current_price_ttl=60, max_retries=3)
        >>> provider = CachedMarketDataProvider(base_provider, config)
        >>> 
        >>> # First call hits API
        >>> price1 = await provider.get_current_price("AAPL")
        >>> 
        >>> # Second call within 60s uses cache (no API call)
        >>> price2 = await provider.get_current_price("AAPL")
        >>> 
        >>> # If API fails, returns stale data
        >>> price3 = await provider.get_current_price("AAPL")  # API down
        >>> assert price3.is_stale == True
    """
    
    def __init__(
        self,
        underlying_provider: MarketDataProvider,
        config: Optional[CacheConfig] = None,
        cache: Optional[MemoryCache] = None,
    ):
        """
        Initialize cached provider.
        
        Args:
            underlying_provider: Base provider to wrap (e.g., YahooMarketDataProvider)
            config: Cache configuration (uses defaults if None)
            cache: Custom cache instance (creates new if None)
        """
        self._provider = underlying_provider
        self._config = config or CacheConfig()
        self._cache = cache or MemoryCache(
            maxsize=self._config.cache_maxsize,
            default_ttl=self._config.current_price_ttl,
        )
    
    @property
    def source_name(self) -> str:
        """Return underlying provider's source name."""
        return f"{self._provider.source_name}+cached"
    
    @property
    def supports_realtime(self) -> bool:
        """Return underlying provider's realtime support."""
        return self._provider.supports_realtime
    
    @property
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return self._cache.stats()
    
    async def get_current_price(self, symbol: str) -> PriceData:
        """
        Get current price with caching and retry.
        
        Flow:
        1. Check cache (TTL: 60s)
        2. If miss, call underlying provider with retry
        3. If all retries fail, return stale cache if available
        4. Cache successful result
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            PriceData (may have is_stale=True if from stale cache)
        
        Raises:
            SymbolNotFoundError: If symbol invalid and no stale data
            DataUnavailableError: If API down and no stale data
        """
        cache_key = CacheKeyBuilder.price(symbol)
        
        # Try fresh cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT for {symbol} current price")
            return cached
        
        logger.debug(f"Cache MISS for {symbol} current price")
        
        # Execute with retry
        try:
            result = await self._execute_with_retry(
                self._provider.get_current_price,
                symbol,
            )
            
            # Cache successful result
            self._cache.set(
                cache_key,
                result,
                ttl=self._config.current_price_ttl,
            )
            return result
        
        except Exception as e:
            # Try stale fallback
            logger.warning(
                f"Failed to get current price for {symbol} after retries. "
                f"Attempting stale fallback. Error: {e}"
            )
            return self._get_stale_fallback(cache_key, symbol, "current price")
    
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: DateType,
        end_date: DateType,
        interval: str = "1d",
    ) -> List[PriceData]:
        """
        Get historical prices with caching and retry.
        
        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            interval: Data interval
        
        Returns:
            List of PriceData
        """
        cache_key = CacheKeyBuilder.historical(
            symbol,
            str(start_date),
            str(end_date),
            interval,
        )
        
        # Try fresh cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT for {symbol} historical {start_date}-{end_date}")
            return cached
        
        logger.debug(f"Cache MISS for {symbol} historical")
        
        # Execute with retry
        try:
            result = await self._execute_with_retry(
                self._provider.get_historical_prices,
                symbol,
                start_date,
                end_date,
                interval,
            )
            
            # Cache successful result
            self._cache.set(
                cache_key,
                result,
                ttl=self._config.historical_price_ttl,
            )
            return result
        
        except Exception as e:
            # Try stale fallback
            logger.warning(
                f"Failed to get historical prices for {symbol}. "
                f"Attempting stale fallback. Error: {e}"
            )
            return self._get_stale_fallback(cache_key, symbol, "historical prices")
    
    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """
        Get fundamentals with caching and retry.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            FundamentalsData
        """
        cache_key = CacheKeyBuilder.fundamentals(symbol)
        
        # Try fresh cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT for {symbol} fundamentals")
            return cached
        
        logger.debug(f"Cache MISS for {symbol} fundamentals")
        
        # Execute with retry
        try:
            result = await self._execute_with_retry(
                self._provider.get_fundamentals,
                symbol,
            )
            
            # Cache successful result
            self._cache.set(
                cache_key,
                result,
                ttl=self._config.fundamentals_ttl,
            )
            return result
        
        except Exception as e:
            # Try stale fallback
            logger.warning(
                f"Failed to get fundamentals for {symbol}. "
                f"Attempting stale fallback. Error: {e}"
            )
            return self._get_stale_fallback(cache_key, symbol, "fundamentals")
    
    async def search_symbol(self, query: str) -> List[dict]:
        """
        Search symbols (no caching for search - always fresh).
        
        Args:
            query: Search query
        
        Returns:
            List of symbol matches
        """
        # Search results not cached (they change frequently)
        return await self._provider.search_symbol(query)
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with exponential backoff retry.
        
        Retries on:
        - asyncio.TimeoutError
        - RateLimitExceededError
        - Any MarketDataProviderError with HTTP 5xx
        
        Args:
            func: Async function to execute
            *args, **kwargs: Function arguments
        
        Returns:
            Function result
        
        Raises:
            Exception: Last exception if all retries exhausted
        """
        last_exception = None
        backoff_delay = self._config.initial_backoff
        
        for attempt in range(self._config.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{self._config.max_retries + 1}. "
                    f"Retrying in {backoff_delay}s..."
                )
            
            except RateLimitExceededError as e:
                last_exception = e
                # Use retry_after from exception if available
                retry_after = getattr(e, 'retry_after', backoff_delay)
                logger.warning(
                    f"Rate limit hit on attempt {attempt + 1}/{self._config.max_retries + 1}. "
                    f"Retrying in {retry_after}s..."
                )
                backoff_delay = min(retry_after, self._config.max_backoff)
            
            except MarketDataProviderError as e:
                last_exception = e
                # Retry on:
                # - DataUnavailableError (no status_code)
                # - Server errors (5xx status_code)
                # Don't retry on:
                # - Client errors (4xx status_code)
                # - SymbolNotFoundError (inherits from MarketDataProviderError)
                
                if hasattr(e, 'status_code'):
                    # Has status code - check if retriable
                    if 500 <= e.status_code < 600:
                        logger.warning(
                            f"Server error on attempt {attempt + 1}/{self._config.max_retries + 1}. "
                            f"Retrying in {backoff_delay}s..."
                        )
                    else:
                        # Client error (4xx) - don't retry
                        raise
                else:
                    # No status code - treat as retriable (e.g., network error, timeout)
                    logger.warning(
                        f"Provider error on attempt {attempt + 1}/{self._config.max_retries + 1}: {e}. "
                        f"Retrying in {backoff_delay}s..."
                    )
            
            except Exception as e:
                # Unexpected errors - don't retry
                logger.error(f"Unexpected error: {e}")
                raise
            
            # If this wasn't the last attempt, sleep and retry
            if attempt < self._config.max_retries:
                await asyncio.sleep(backoff_delay)
                backoff_delay = min(
                    backoff_delay * self._config.backoff_multiplier,
                    self._config.max_backoff,
                )
            else:
                # Last attempt failed
                break
        
        # All retries exhausted
        if last_exception:
            raise last_exception
    
    def _get_stale_fallback(self, cache_key: str, symbol: str, data_type: str):
        """
        Try to return stale cached data as fallback.
        
        Args:
            cache_key: Cache key to look up
            symbol: Symbol for error message
            data_type: Data type description for error message
        
        Returns:
            Stale cached data with is_stale=True
        
        Raises:
            DataUnavailableError: If no stale data available
        """
        # Try to get stale data
        stale_data = self._cache.get(cache_key, allow_stale=True)
        
        if stale_data is not None:
            logger.info(
                f"Returning STALE cached {data_type} for {symbol} "
                f"(API unavailable)"
            )
            
            # Mark data as stale
            if isinstance(stale_data, (PriceData, FundamentalsData)):
                # Use model_copy to create new instance with is_stale=True
                return stale_data.model_copy(update={"is_stale": True})
            elif isinstance(stale_data, list) and len(stale_data) > 0:
                # For historical data (list of PriceData)
                return [
                    item.model_copy(update={"is_stale": True})
                    if isinstance(item, PriceData)
                    else item
                    for item in stale_data
                ]
            else:
                # Fallback for other types
                return stale_data
        
        # No stale data available - raise error
        from src.market_data.domain.providers import DataUnavailableError
        raise DataUnavailableError(
            f"No fresh or stale {data_type} available for {symbol}. "
            f"API is unavailable and cache is empty.",
            self._provider.source_name
        )
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of items in cache."""
        return self._cache.size()
