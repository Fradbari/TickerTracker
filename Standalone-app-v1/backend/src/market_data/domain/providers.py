"""
Market Data Providers - Abstract interface for data sources.

This module defines the abstract interface for market data providers,
decoupling business logic from specific data sources (Yahoo, Finnhub, etc.).
"""

from abc import ABC, abstractmethod
from datetime import date as DateType
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# DATA CONTRACTS
# ============================================================================

class PriceData(BaseModel):
    """
    Price data contract for a single point in time.

    Used as the standard internal format for price data regardless of source.
    All providers must return data in this format.

    Attributes:
        symbol: Ticker symbol (e.g., "AAPL")
        date: Date of the data point
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        adjusted_close: Adjusted closing price (optional)
        source: Data source identifier
        timestamp: When this data was retrieved
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "date": "2024-01-15",
                "open": "182.50",
                "high": "184.20",
                "low": "181.80",
                "close": "183.90",
                "volume": 52000000,
                "adjusted_close": "183.45",
                "source": "yahoo",
                "timestamp": "2024-01-15T21:00:00Z",
            }
        }
    )

    symbol: str = Field(..., description="Ticker symbol")
    date: DateType = Field(..., description="Date of the data point")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    adjusted_close: Decimal | None = Field(None, description="Adjusted close price")
    source: str = Field(..., description="Data source identifier")
    timestamp: datetime = Field(..., description="When data was retrieved")
    is_stale: bool = Field(False, description="Whether this data is from stale cache")


class FundamentalsData(BaseModel):
    """
    Fundamental data contract for a company.

    Contains key financial metrics and company information.
    Not all fields may be available from all providers.

    Attributes:
        symbol: Ticker symbol
        company_name: Company official name
        sector: Business sector
        industry: Industry classification
        market_cap: Market capitalization
        pe_ratio: Price-to-earnings ratio
        eps: Earnings per share
        dividend_yield: Dividend yield percentage
        beta: Stock beta (volatility measure)
        fifty_two_week_high: 52-week high price
        fifty_two_week_low: 52-week low price
        average_volume: Average daily trading volume
        source: Data source identifier
        timestamp: When data was retrieved
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": "2850000000000",
                "pe_ratio": "28.5",
                "eps": "6.45",
                "dividend_yield": "0.52",
                "beta": "1.25",
                "fifty_two_week_high": "198.23",
                "fifty_two_week_low": "164.08",
                "average_volume": 54000000,
                "source": "yahoo",
                "timestamp": "2024-01-15T21:00:00Z",
            }
        }
    )

    symbol: str = Field(..., description="Ticker symbol")
    company_name: str | None = Field(None, description="Company name")
    sector: str | None = Field(None, description="Business sector")
    industry: str | None = Field(None, description="Industry classification")
    market_cap: Decimal | None = Field(None, description="Market capitalization")
    pe_ratio: Decimal | None = Field(None, description="Price-to-earnings ratio")
    eps: Decimal | None = Field(None, description="Earnings per share")
    dividend_yield: Decimal | None = Field(None, description="Dividend yield %")
    beta: Decimal | None = Field(None, description="Stock beta")
    fifty_two_week_high: Decimal | None = Field(None, description="52-week high")
    fifty_two_week_low: Decimal | None = Field(None, description="52-week low")
    average_volume: int | None = Field(None, description="Average daily volume")
    source: str = Field(..., description="Data source identifier")
    timestamp: datetime = Field(..., description="When data was retrieved")
    is_stale: bool = Field(False, description="Whether this data is from stale cache")


# ============================================================================
# ABSTRACT PROVIDER INTERFACE
# ============================================================================

class MarketDataProvider(ABC):
    """
    Abstract interface for market data providers.

    All concrete providers must implement these methods.
    This allows the application to switch between data sources
    (Yahoo Finance, Finnhub, Alpha Vantage, etc.) without changing
    business logic.

    Design principles:
    - Methods should be async for network I/O
    - All prices returned as Decimal for precision
    - Consistent error handling (raise specific exceptions)
    - Rate limiting handled internally by each provider
    """

    @abstractmethod
    async def get_current_price(self, symbol: str) -> PriceData:
        """
        Get the current/most recent price for a symbol.

        This should return the latest available data point.
        For real-time providers, this is current market data.
        For delayed providers, this is the most recent close.

        Args:
            symbol: Ticker symbol (e.g., "AAPL", "MSFT")

        Returns:
            PriceData with current price information

        Raises:
            ValueError: If symbol is invalid
            RuntimeError: If data source unavailable
        """
        pass

    @abstractmethod
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: DateType,
        end_date: DateType,
        interval: str = "1d",
    ) -> list[PriceData]:
        """
        Get historical price data for a symbol.

        Args:
            symbol: Ticker symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            interval: Data interval ("1d", "1h", "1m", etc.)
                     Supported intervals vary by provider

        Returns:
            List of PriceData ordered by date ascending

        Raises:
            ValueError: If symbol invalid or date range invalid
            RuntimeError: If data source unavailable
        """
        pass

    @abstractmethod
    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """
        Get fundamental data for a symbol.

        Returns key financial metrics and company information.
        Not all fields may be available from all providers.

        Args:
            symbol: Ticker symbol

        Returns:
            FundamentalsData with available metrics

        Raises:
            ValueError: If symbol is invalid
            RuntimeError: If data source unavailable
        """
        pass

    @abstractmethod
    async def search_symbol(self, query: str) -> list[dict]:
        """
        Search for ticker symbols matching a query.

        Useful for autocomplete and symbol discovery.

        Args:
            query: Search query (company name or symbol fragment)

        Returns:
            List of dicts with symbol matches, e.g.:
            [
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
                {"symbol": "AAPLW", "name": "Apple Warrant", "exchange": "NASDAQ"}
            ]

        Raises:
            RuntimeError: If data source unavailable
        """
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Identifier for this data source.

        Returns:
            Source name (e.g., "yahoo", "finnhub", "alphavantage")
        """
        pass

    @property
    @abstractmethod
    def supports_realtime(self) -> bool:
        """
        Whether this provider supports real-time data.

        Returns:
            True if real-time, False if delayed (15-20 minutes)
        """
        pass


# ============================================================================
# EXCEPTIONS
# ============================================================================

class MarketDataProviderError(Exception):
    """Base exception for market data provider errors."""
    pass


class SymbolNotFoundError(MarketDataProviderError):
    """Raised when a ticker symbol is not found."""

    def __init__(self, symbol: str, provider: str):
        self.symbol = symbol
        self.provider = provider
        super().__init__(f"Symbol '{symbol}' not found in {provider}")


class DataUnavailableError(MarketDataProviderError):
    """Raised when data is temporarily unavailable."""

    def __init__(self, message: str, provider: str):
        self.provider = provider
        super().__init__(f"{provider}: {message}")


class RateLimitExceededError(MarketDataProviderError):
    """Raised when provider rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None):
        self.provider = provider
        self.retry_after = retry_after
        msg = f"{provider}: Rate limit exceeded"
        if retry_after:
            msg += f". Retry after {retry_after} seconds"
        super().__init__(msg)
