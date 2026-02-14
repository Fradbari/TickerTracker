"""
Market Data Service - Business logic for market data operations.

This service orchestrates market data operations using the injected
MarketDataProvider for external data and MarketDataRepository for
persistence.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.market_data.domain.providers import (
    MarketDataProvider,
    PriceData,
    FundamentalsData,
    SymbolNotFoundError,
    DataUnavailableError,
)
from src.market_data.repositories.market_data_repository import (
    MarketDataRepository,
    MarketDataRow,
)
from src.market_data.domain.entities import Ticker


class MarketDataService:
    """
    Service for market data operations.
    
    Responsibilities:
    - Fetch data from external providers
    - Store data in repository
    - Sync/update historical data
    - Provide unified interface for market data access
    
    The service uses dependency injection to decouple from specific
    data sources, allowing easy swapping between Yahoo, Finnhub, etc.
    """
    
    def __init__(
        self,
        provider: MarketDataProvider,
        repository: MarketDataRepository,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """
        Initialize service with dependencies.
        
        Args:
            provider: Market data provider (Yahoo, Finnhub, etc.)
            repository: Repository for data persistence
            session_factory: Database session factory
        """
        self._provider = provider
        self._repository = repository
        self._session_factory = session_factory
    
    async def get_current_price(self, ticker_id: UUID) -> Decimal:
        """
        Get current price for a ticker.
        
        First tries to get from repository (cached data).
        If not available or stale, fetches from provider.
        
        Args:
            ticker_id: Ticker UUID
            
        Returns:
            Current price as Decimal
            
        Raises:
            ValueError: Ticker not found
            RuntimeError: Data unavailable
        """
        # Get ticker to get symbol
        ticker = await self._get_ticker(ticker_id)
        if not ticker:
            raise ValueError(f"Ticker {ticker_id} not found")
        
        # Try to get latest from repository first
        latest = await self._repository.get_latest_price(ticker_id)
        
        # If we have recent data (today), use it
        if latest and latest.date == date.today():
            return latest.close
        
        # Otherwise fetch from provider
        try:
            price_data = await self._provider.get_current_price(ticker.symbol)
            
            # Store in repository
            await self._store_price_data(ticker_id, [price_data])
            
            return price_data.close
            
        except SymbolNotFoundError as e:
            raise ValueError(f"Symbol '{ticker.symbol}' not found: {e}")
        except DataUnavailableError as e:
            raise RuntimeError(f"Market data unavailable: {e}")
    
    async def sync_historical_data(
        self,
        ticker_id: UUID,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> int:
        """
        Sync historical data from provider to repository.
        
        Fetches data from external provider and stores in database.
        Uses upsert to handle overlapping data gracefully.
        
        Args:
            ticker_id: Ticker UUID
            start_date: Start date
            end_date: End date
            interval: Data interval (default "1d")
            
        Returns:
            Number of rows synced
            
        Raises:
            ValueError: Ticker not found
            RuntimeError: Data unavailable
        """
        # Get ticker symbol
        ticker = await self._get_ticker(ticker_id)
        if not ticker:
            raise ValueError(f"Ticker {ticker_id} not found")
        
        try:
            # Fetch historical data
            price_data_list = await self._provider.get_historical_prices(
                symbol=ticker.symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
            )
            
            if not price_data_list:
                return 0
            
            # Store in repository
            return await self._store_price_data(ticker_id, price_data_list)
            
        except SymbolNotFoundError as e:
            raise ValueError(f"Symbol '{ticker.symbol}' not found: {e}")
        except DataUnavailableError as e:
            raise RuntimeError(f"Market data unavailable: {e}")
    
    async def get_fundamentals(self, ticker_id: UUID) -> FundamentalsData:
        """
        Get fundamental data for a ticker.
        
        Fetches from provider (no caching currently).
        
        Args:
            ticker_id: Ticker UUID
            
        Returns:
            FundamentalsData
            
        Raises:
            ValueError: Ticker not found
            RuntimeError: Data unavailable
        """
        ticker = await self._get_ticker(ticker_id)
        if not ticker:
            raise ValueError(f"Ticker {ticker_id} not found")
        
        try:
            return await self._provider.get_fundamentals(ticker.symbol)
            
        except SymbolNotFoundError as e:
            raise ValueError(f"Symbol '{ticker.symbol}' not found: {e}")
        except DataUnavailableError as e:
            raise RuntimeError(f"Market data unavailable: {e}")
    
    async def search_symbols(self, query: str) -> List[dict]:
        """
        Search for ticker symbols.
        
        Uses provider's search functionality.
        
        Args:
            query: Search query
            
        Returns:
            List of matching symbols with metadata
        """
        try:
            return await self._provider.search_symbol(query)
        except Exception as e:
            raise RuntimeError(f"Symbol search failed: {e}")
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _get_ticker(self, ticker_id: UUID) -> Optional[Ticker]:
        """Get ticker entity by ID."""
        async with self._session_factory() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Ticker).where(Ticker.id == ticker_id)
            )
            return result.scalar_one_or_none()
    
    async def _store_price_data(
        self,
        ticker_id: UUID,
        price_data_list: List[PriceData],
    ) -> int:
        """
        Store list of PriceData in repository.
        
        Converts PriceData to MarketDataRow format and upserts.
        
        Args:
            ticker_id: Ticker UUID
            price_data_list: List of PriceData to store
            
        Returns:
            Number of rows stored
        """
        if not price_data_list:
            return 0
        
        # Convert PriceData to MarketDataRow
        rows = [
            MarketDataRow(
                ticker_id=ticker_id,
                date=pd.date,
                open=pd.open,
                high=pd.high,
                low=pd.low,
                close=pd.close,
                volume=pd.volume,
                data_source=pd.source,
                quality_score=Decimal("0.80"),  # Default quality score
            )
            for pd in price_data_list
        ]
        
        # Upsert to repository
        return await self._repository.upsert_daily(ticker_id, rows)
