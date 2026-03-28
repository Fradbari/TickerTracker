"""
Fake and stub market data providers for testing and future expansion.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from src.market_data.domain.providers import (
    DataUnavailableError,
    FundamentalsData,
    MarketDataProvider,
    PriceData,
    SymbolNotFoundError,
)


class FakeMarketDataProvider(MarketDataProvider):
    """
    Fake provider for testing purposes.

    Returns predictable, configurable data without external calls.
    Useful for unit tests and development.

    Usage:
        >>> provider = FakeMarketDataProvider()
        >>> provider.set_price("AAPL", Decimal("150.00"))
        >>> price = await provider.get_current_price("AAPL")
        >>> assert price.close == Decimal("150.00")
    """

    def __init__(self):
        """Initialize with empty data."""
        self._prices: dict[str, Decimal] = {}
        self._fundamentals: dict[str, FundamentalsData] = {}
        self._fail_on: str | None = None  # Symbol to fail on for error testing

    def set_price(self, symbol: str, price: Decimal) -> None:
        """Set current price for a symbol."""
        self._prices[symbol.upper()] = price

    def set_fundamentals(self, symbol: str, data: FundamentalsData) -> None:
        """Set fundamental data for a symbol."""
        self._fundamentals[symbol.upper()] = data

    def fail_on_symbol(self, symbol: str) -> None:
        """Make provider fail when this symbol is requested."""
        self._fail_on = symbol.upper()

    def reset(self) -> None:
        """Clear all configured data."""
        self._prices.clear()
        self._fundamentals.clear()
        self._fail_on = None

    async def get_current_price(self, symbol: str) -> PriceData:
        """Get configured current price."""
        symbol = symbol.upper()

        if symbol == self._fail_on:
            raise DataUnavailableError("Simulated failure", "fake")

        if symbol not in self._prices:
            raise SymbolNotFoundError(symbol, "fake")

        price = self._prices[symbol]

        return PriceData(
            symbol=symbol,
            date=date.today(),
            open=price,
            high=price * Decimal("1.02"),
            low=price * Decimal("0.98"),
            close=price,
            volume=1000000,
            adjusted_close=price,
            source="fake",
            timestamp=datetime.now(UTC),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> list[PriceData]:
        """Generate fake historical prices."""
        symbol = symbol.upper()

        if symbol == self._fail_on:
            raise DataUnavailableError("Simulated failure", "fake")

        if symbol not in self._prices:
            raise SymbolNotFoundError(symbol, "fake")

        base_price = self._prices[symbol]
        result = []

        # Generate daily data
        current_date = start_date
        while current_date <= end_date:
            # Add slight variation each day
            variation = Decimal(str((hash(current_date) % 100) / 1000.0))
            day_price = base_price * (Decimal("1.0") + variation)

            result.append(
                PriceData(
                    symbol=symbol,
                    date=current_date,
                    open=day_price,
                    high=day_price * Decimal("1.02"),
                    low=day_price * Decimal("0.98"),
                    close=day_price,
                    volume=1000000,
                    adjusted_close=day_price,
                    source="fake",
                    timestamp=datetime.now(UTC),
                )
            )

            current_date += timedelta(days=1)

        return result

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """Get configured fundamentals."""
        symbol = symbol.upper()

        if symbol == self._fail_on:
            raise DataUnavailableError("Simulated failure", "fake")

        if symbol in self._fundamentals:
            return self._fundamentals[symbol]

        # Return default fundamentals
        return FundamentalsData(
            symbol=symbol,
            company_name=f"{symbol} Test Company",
            sector="Technology",
            industry="Software",
            market_cap=Decimal("1000000000"),
            pe_ratio=Decimal("25.0"),
            eps=Decimal("5.0"),
            dividend_yield=Decimal("1.5"),
            beta=Decimal("1.2"),
            fifty_two_week_high=Decimal("200.0"),
            fifty_two_week_low=Decimal("150.0"),
            average_volume=5000000,
            source="fake",
            timestamp=datetime.now(UTC),
        )

    async def search_symbol(self, query: str) -> list[dict]:
        """Return configured symbols matching query."""
        query = query.upper()

        matches = []
        for symbol in self._prices.keys():
            if query in symbol:
                matches.append({
                    "symbol": symbol,
                    "name": f"{symbol} Test Company",
                    "exchange": "TEST",
                })

        return matches

    @property
    def source_name(self) -> str:
        return "fake"

    @property
    def supports_realtime(self) -> bool:
        return True  # Fake provider is "instant"


# ============================================================================
# STUB PROVIDERS FOR FUTURE IMPLEMENTATION
# ============================================================================

class FinnhubMarketDataProvider(MarketDataProvider):
    """
    Stub for Finnhub.io provider.

    Finnhub offers:
    - Real-time data for US markets
    - Global market coverage
    - Fundamental data
    - News and social sentiment
    - Free tier: 60 API calls/minute

    TODO: Implement using finnhub-python library
    Docs: https://finnhub.io/docs/api
    """

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self._api_key = api_key
        raise NotImplementedError(
            "FinnhubMarketDataProvider not yet implemented. "
            "Use YahooMarketDataProvider or contribute implementation!"
        )

    async def get_current_price(self, symbol: str) -> PriceData:
        raise NotImplementedError()

    async def get_historical_prices(
        self, symbol: str, start_date: date, end_date: date, interval: str = "1d"
    ) -> list[PriceData]:
        raise NotImplementedError()

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        raise NotImplementedError()

    async def search_symbol(self, query: str) -> list[dict]:
        raise NotImplementedError()

    @property
    def source_name(self) -> str:
        return "finnhub"

    @property
    def supports_realtime(self) -> bool:
        return True


class AlphaVantageMarketDataProvider(MarketDataProvider):
    """
    Stub for Alpha Vantage provider.

    Alpha Vantage offers:
    - Real-time and historical data
    - Technical indicators
    - Fundamental data
    - Cryptocurrency data
    - Free tier: 5 API calls/minute, 500/day

    TODO: Implement using alpha-vantage library
    Docs: https://www.alphavantage.co/documentation/
    """

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self._api_key = api_key
        raise NotImplementedError(
            "AlphaVantageMarketDataProvider not yet implemented. "
            "Use YahooMarketDataProvider or contribute implementation!"
        )

    async def get_current_price(self, symbol: str) -> PriceData:
        raise NotImplementedError()

    async def get_historical_prices(
        self, symbol: str, start_date: date, end_date: date, interval: str = "1d"
    ) -> list[PriceData]:
        raise NotImplementedError()

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        raise NotImplementedError()

    async def search_symbol(self, query: str) -> list[dict]:
        raise NotImplementedError()

    @property
    def source_name(self) -> str:
        return "alphavantage"

    @property
    def supports_realtime(self) -> bool:
        return True


class PolygonMarketDataProvider(MarketDataProvider):
    """
    Stub for Polygon.io provider.

    Polygon offers:
    - Real-time and historical data
    - Options and crypto data
    - Aggregated bars at multiple timeframes
    - Excellent data quality
    - Free tier: delayed data, 5 API calls/minute

    TODO: Implement using polygon-api-client library
    Docs: https://polygon.io/docs/stocks/getting-started
    """

    def __init__(self, api_key: str):
        """Initialize with API key."""
        self._api_key = api_key
        raise NotImplementedError(
            "PolygonMarketDataProvider not yet implemented. "
            "Use YahooMarketDataProvider or contribute implementation!"
        )

    async def get_current_price(self, symbol: str) -> PriceData:
        raise NotImplementedError()

    async def get_historical_prices(
        self, symbol: str, start_date: date, end_date: date, interval: str = "1d"
    ) -> list[PriceData]:
        raise NotImplementedError()

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        raise NotImplementedError()

    async def search_symbol(self, query: str) -> list[dict]:
        raise NotImplementedError()

    @property
    def source_name(self) -> str:
        return "polygon"

    @property
    def supports_realtime(self) -> bool:
        return True
