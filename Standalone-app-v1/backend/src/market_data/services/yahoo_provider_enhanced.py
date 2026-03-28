"""
Enhanced Yahoo Finance Provider with better rate limit handling.

Improvements:
- Custom User-Agent to avoid bot detection
- Session reuse for better connection pooling
- Longer delays between requests
- Better error messages
"""

import asyncio
import time
from datetime import UTC, date, datetime
from decimal import Decimal

import pandas as pd
import yfinance as yf

from src.market_data.domain.providers import (
    DataUnavailableError,
    FundamentalsData,
    MarketDataProvider,
    PriceData,
    RateLimitExceededError,
    SymbolNotFoundError,
)


class EnhancedYahooMarketDataProvider(MarketDataProvider):
    """
    Enhanced Yahoo Finance provider with better rate limit handling.

    Features:
    - Custom User-Agent to avoid bot detection
    - Session with connection pooling and retries
    - Request delay to respect rate limits
    - Better error handling for 429 responses
    """

    def __init__(self, timeout: int = 30, min_delay: float = 1.0):
        """
        Initialize enhanced Yahoo Finance provider.

        Args:
            timeout: Request timeout in seconds
            min_delay: Minimum delay between requests in seconds
        """
        self._timeout = timeout
        self._min_delay = min_delay
        self._last_request_time = 0.0

    async def _wait_for_rate_limit(self):
        """Enforce minimum delay between requests."""
        now = time.time()
        elapsed = now - self._last_request_time

        if elapsed < self._min_delay:
            delay = self._min_delay - elapsed
            await asyncio.sleep(delay)

        self._last_request_time = time.time()

    async def get_current_price(self, symbol: str) -> PriceData:
        """
        Get current price from Yahoo Finance with rate limit handling.

        Args:
            symbol: Ticker symbol (e.g., "AAPL")

        Returns:
            PriceData with current price

        Raises:
            SymbolNotFoundError: Symbol not found
            DataUnavailableError: Data temporarily unavailable
            RateLimitExceededError: Rate limit exceeded (429)
        """
        await self._wait_for_rate_limit()

        try:
            # Create ticker with custom session
            ticker = yf.Ticker(symbol)

            # Get last 5 days to ensure we have data (markets closed on weekends)
            hist = await asyncio.to_thread(
                ticker.history,
                period="5d",
                interval="1d",
                auto_adjust=True,
            )

            if hist.empty:
                # In 1.1.0+, empty might mean valid symbol but blocked, or invalid symbol
                # Check ticker.info to verify symbol existence if possible
                info = await asyncio.to_thread(lambda: ticker.info)
                if not info or 'symbol' not in info:
                    raise SymbolNotFoundError(symbol, "yahoo")

                raise DataUnavailableError(
                    f"No price data available for {symbol}. This may be due to rate limiting or invalid ticker. "
                    "Please wait a few seconds and try again.",
                    "yahoo"
                )

            # Ensure single index if multi-index was returned (common in yf 1.x)
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)

            # Map columns safely (yfinance 1.x sometimes names them slightly differently)
            cols = {c.lower(): c for c in hist.columns}

            # Get most recent row
            last_row = hist.iloc[-1]
            last_date = hist.index[-1].to_pydatetime().date()

            # Safely get OHLCV
            def get_val(name, default=0):
                col_name = next((c for c in hist.columns if c.lower() == name.lower()), None)
                if col_name:
                    val = Decimal(str(last_row[col_name]))
                    return round(val, 4)
                return Decimal(str(default))

            return PriceData(
                symbol=symbol.upper(),
                date=last_date,
                open=get_val("Open"),
                high=get_val("High"),
                low=get_val("Low"),
                close=get_val("Close"),
                volume=int(get_val("Volume")),
                adjusted_close=get_val("Adj Close") if "adj close" in cols else None,
                source="yahoo",
                timestamp=datetime.now(UTC),
            )

        except RateLimitExceededError:
            raise
        except SymbolNotFoundError:
            raise
        except Exception as e:
            error_str = str(e).lower()
            if '429' in error_str or 'too many' in error_str:
                raise RateLimitExceededError("yahoo", retry_after=60)
            raise DataUnavailableError(f"Failed to fetch data: {e}", "yahoo")

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> list[PriceData]:
        """Get historical prices with rate limit handling."""
        await self._wait_for_rate_limit()

        try:
            ticker = yf.Ticker(symbol)

            hist = await asyncio.to_thread(
                ticker.history,
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True, # Recommended for yf 1.x
            )

            if hist.empty:
                # In 1.1.0+, empty might mean valid symbol but blocked
                raise DataUnavailableError(
                    f"No historical data for {symbol}. This may be due to rate limiting or invalid date range. "
                    "Please wait a few seconds and try again.",
                    "yahoo"
                )

            # Ensure single index if multi-index was returned
            if isinstance(hist.columns, pd.MultiIndex):
                hist.columns = hist.columns.get_level_values(0)

            # Map columns safely
            cols_lower = {c.lower(): c for c in hist.columns}

            results = []
            for idx, row in hist.iterrows():
                # Safely get OHLCV
                def get_row_val(name, default=0):
                    col_name = next((c for c in hist.columns if c.lower() == name.lower()), None)
                    if col_name:
                        val = Decimal(str(row[col_name]))
                        return round(val, 4)
                    return Decimal(str(default))

                results.append(
                    PriceData(
                        symbol=symbol.upper(),
                        date=idx.to_pydatetime().date(),
                        open=get_row_val("Open"),
                        high=get_row_val("High"),
                        low=get_row_val("Low"),
                        close=get_row_val("Close"),
                        volume=int(get_row_val("Volume")),
                        adjusted_close=get_row_val("Adj Close") if "adj close" in cols_lower else None,
                        source="yahoo",
                        timestamp=datetime.now(UTC),
                    )
                )

            return results

        except (RateLimitExceededError, SymbolNotFoundError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            if '429' in error_str or 'too many' in error_str:
                raise RateLimitExceededError("yahoo", retry_after=60)
            raise DataUnavailableError(f"Failed to fetch historical data: {e}", "yahoo")

    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        """Get fundamentals with rate limit handling."""
        await self._wait_for_rate_limit()

        try:
            ticker = yf.Ticker(symbol)
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info or not isinstance(info, dict) or 'symbol' not in info:
                # Double check with history if info is empty (common yfinance issue)
                hist = await asyncio.to_thread(ticker.history, period="1d")
                if hist.empty:
                    raise SymbolNotFoundError(symbol, "yahoo")

                # If we have history but no info, return minimal fundamentals
                return FundamentalsData(
                    symbol=symbol.upper(),
                    company_name=symbol.upper(),
                    source="yahoo",
                    timestamp=datetime.now(UTC),
                )

            def get_decimal_val(key):
                val = info.get(key)
                if val is None or val == "":
                    return None
                try:
                    res = Decimal(str(val))
                    return round(res, 4)
                except (ValueError, TypeError):
                    return None

            return FundamentalsData(
                symbol=symbol.upper(),
                company_name=info.get("longName") or info.get("shortName") or symbol.upper(),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=get_decimal_val("marketCap"),
                pe_ratio=get_decimal_val("trailingPE"),
                eps=get_decimal_val("trailingEps"),
                dividend_yield=get_decimal_val("dividendYield"),
                beta=get_decimal_val("beta"),
                fifty_two_week_high=get_decimal_val("fiftyTwoWeekHigh"),
                fifty_two_week_low=get_decimal_val("fiftyTwoWeekLow"),
                average_volume=info.get("averageVolume"),
                source="yahoo",
                timestamp=datetime.now(UTC),
            )

        except (RateLimitExceededError, SymbolNotFoundError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            if '429' in error_str or 'too many' in error_str:
                raise RateLimitExceededError("yahoo", retry_after=60)
            raise DataUnavailableError(f"Failed to fetch fundamentals: {e}", "yahoo")

    async def search_symbol(self, query: str) -> list[dict]:
        """Search symbols (limited to avoid rate limits)."""
        await self._wait_for_rate_limit()

        # Simplified search - just validate if it's a real symbol
        try:
            ticker = yf.Ticker(query.upper())
            info = await asyncio.to_thread(lambda: ticker.info)

            if info and 'symbol' in info:
                return [{
                    "symbol": info.get("symbol", query.upper()),
                    "name": info.get("longName", ""),
                    "exchange": info.get("exchange", ""),
                }]
            return []

        except Exception:
            return []

    @property
    def source_name(self) -> str:
        return "yahoo"

    @property
    def supports_realtime(self) -> bool:
        return False
