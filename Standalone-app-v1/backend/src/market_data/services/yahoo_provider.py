"""
Yahoo Finance Market Data Provider implementation.

Concrete implementation of MarketDataProvider using yfinance library.
"""

import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal

import yfinance as yf

from src.market_data.domain.providers import (
    DataUnavailableError,
    FundamentalsData,
    MarketDataProvider,
    PriceData,
    SymbolNotFoundError,
)


class YahooMarketDataProvider(MarketDataProvider):
    """
    Yahoo Finance data provider implementation.

    Uses yfinance library to fetch data from Yahoo Finance API.
    Free and reliable, but with delayed data (15-20 minutes).

    Features:
    - Historical data going back decades
    - Good coverage of global markets
    - Fundamental data available
    - No API key required
    - Rate limiting handled by backoff

    Limitations:
    - Data is delayed (not real-time)
    - Rate limits can be hit with heavy usage
    - Some symbols may have incomplete data
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize Yahoo Finance provider.

        Args:
            timeout: Request timeout in seconds
        """
        self._timeout = timeout

    async def get_current_price(self, symbol: str) -> PriceData:
        """
        Get current price from Yahoo Finance.

        Fetches the most recent trading day data.

        Args:
            symbol: Ticker symbol (e.g., "AAPL")

        Returns:
            PriceData with current price

        Raises:
            SymbolNotFoundError: Symbol not found
            DataUnavailableError: Data temporarily unavailable
        """
        try:
            # Run blocking yfinance call in executor
            ticker = await asyncio.to_thread(yf.Ticker, symbol)

            # Get last 2 days to ensure we have data
            hist = await asyncio.to_thread(
                ticker.history,
                period="2d",
                interval="1d",
            )

            if hist.empty:
                raise SymbolNotFoundError(symbol, "yahoo")

            # Get most recent row
            last_row = hist.iloc[-1]
            last_date = hist.index[-1].date()

            return PriceData(
                symbol=symbol.upper(),
                date=last_date,
                open=Decimal(str(last_row["Open"])),
                high=Decimal(str(last_row["High"])),
                low=Decimal(str(last_row["Low"])),
                close=Decimal(str(last_row["Close"])),
                volume=int(last_row["Volume"]),
                adjusted_close=None,  # Yahoo doesn't provide adj close in history
                source="yahoo",
                timestamp=datetime.now(UTC),
            )

        except SymbolNotFoundError:
            raise
        except Exception as e:
            raise DataUnavailableError(str(e), "yahoo")

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> list[PriceData]:
        """
        Get historical prices from Yahoo Finance.

        Args:
            symbol: Ticker symbol
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            interval: "1d", "1h", "1m", etc.

        Returns:
            List of PriceData ordered by date

        Raises:
            SymbolNotFoundError: Symbol not found
            DataUnavailableError: Data unavailable
        """
        try:
            ticker = await asyncio.to_thread(yf.Ticker, symbol)

            hist = await asyncio.to_thread(
                ticker.history,
                start=start_date,
                end=end_date,
                interval=interval,
            )

            if hist.empty:
                raise SymbolNotFoundError(symbol, "yahoo")

            # Convert DataFrame to list of PriceData
            result = []
            for idx, row in hist.iterrows():
                price_data = PriceData(
                    symbol=symbol.upper(),
                    date=idx.date(),
                    open=Decimal(str(row["Open"])),
                    high=Decimal(str(row["High"])),
                    low=Decimal(str(row["Low"])),
                    close=Decimal(str(row["Close"])),
                    volume=int(row["Volume"]),
                    adjusted_close=None,
                    source="yahoo",
                    timestamp=datetime.now(UTC),
                )
                result.append(price_data)

            return result

        except SymbolNotFoundError:
            raise
        except Exception as e:
            raise DataUnavailableError(str(e), "yahoo")

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """
        Get fundamental data from Yahoo Finance.

        Args:
            symbol: Ticker symbol

        Returns:
            FundamentalsData with available metrics

        Raises:
            SymbolNotFoundError: Symbol not found
            DataUnavailableError: Data unavailable
        """
        try:
            ticker = await asyncio.to_thread(yf.Ticker, symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info or "symbol" not in info:
                raise SymbolNotFoundError(symbol, "yahoo")

            # Extract available data with safe defaults
            def safe_decimal(key: str) -> Decimal | None:
                value = info.get(key)
                if value is None or value == "N/A":
                    return None
                try:
                    return Decimal(str(value))
                except:
                    return None

            return FundamentalsData(
                symbol=symbol.upper(),
                company_name=info.get("longName") or info.get("shortName"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=safe_decimal("marketCap"),
                pe_ratio=safe_decimal("trailingPE"),
                eps=safe_decimal("trailingEps"),
                dividend_yield=safe_decimal("dividendYield"),
                beta=safe_decimal("beta"),
                fifty_two_week_high=safe_decimal("fiftyTwoWeekHigh"),
                fifty_two_week_low=safe_decimal("fiftyTwoWeekLow"),
                average_volume=info.get("averageVolume"),
                source="yahoo",
                timestamp=datetime.now(UTC),
            )

        except SymbolNotFoundError:
            raise
        except Exception as e:
            raise DataUnavailableError(str(e), "yahoo")

    async def search_symbol(self, query: str) -> list[dict]:
        """
        Search for symbols using Yahoo Finance.

        Note: yfinance doesn't have a built-in search API,
        so this is a basic implementation. Consider using
        a dedicated search provider for production.

        Args:
            query: Search query

        Returns:
            List of matching symbols
        """
        # Basic implementation: try to get info for the query itself
        # A production implementation would use a proper search API
        try:
            ticker = await asyncio.to_thread(yf.Ticker, query)
            info = await asyncio.to_thread(lambda: ticker.info)

            if info and "symbol" in info:
                return [
                    {
                        "symbol": info.get("symbol", query).upper(),
                        "name": info.get("longName") or info.get("shortName", ""),
                        "exchange": info.get("exchange", ""),
                    }
                ]

            return []

        except Exception:
            return []

    @property
    def source_name(self) -> str:
        """Return source identifier."""
        return "yahoo"

    @property
    def supports_realtime(self) -> bool:
        """Yahoo Finance provides delayed data."""
        return False
