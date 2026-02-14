"""
Enhanced Yahoo Finance Provider with better rate limit handling.

Improvements:
- Custom User-Agent to avoid bot detection
- Session reuse for better connection pooling
- Longer delays between requests
- Better error messages
"""

import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
import time

import yfinance as yf
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.market_data.domain.providers import (
    MarketDataProvider,
    PriceData,
    FundamentalsData,
    SymbolNotFoundError,
    DataUnavailableError,
    RateLimitExceededError,
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
    
    def __init__(self, timeout: int = 30, min_delay: float = 0.5):
        """
        Initialize enhanced Yahoo Finance provider.
        
        Args:
            timeout: Request timeout in seconds
            min_delay: Minimum delay between requests in seconds
        """
        self._timeout = timeout
        self._min_delay = min_delay
        self._last_request_time = 0.0
        
        # Create session with custom headers and retry logic
        self._session = self._create_session()
    
    def _create_session(self) -> Session:
        """Create a requests session with optimal settings."""
        session = Session()
        
        # Set user agent to avoid bot detection
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Configure retry strategy (but not for 429 - we handle that separately)
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],  # NOT 429
            allowed_methods=["GET"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=1, pool_maxsize=1)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
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
            ticker = yf.Ticker(symbol, session=self._session)
            
            # Get last 5 days to ensure we have data (markets closed on weekends)
            hist = await asyncio.to_thread(
                ticker.history,
                period="5d",
                interval="1d",
            )
            
            if hist.empty:
                # Empty DataFrame usually indicates rate limiting or invalid symbol
                # Don't make additional requests - assume rate limit for safety
                raise DataUnavailableError(
                    f"No price data available for {symbol}. This may be due to rate limiting. "
                    "Please wait 60 seconds and try again.",
                    "yahoo"
                )
            
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
                adjusted_close=None,
                source="yahoo",
                timestamp=datetime.now(timezone.utc),
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
    ) -> List[PriceData]:
        """Get historical prices with rate limit handling."""
        await self._wait_for_rate_limit()
        
        try:
            ticker = yf.Ticker(symbol, session=self._session)
            
            hist = await asyncio.to_thread(
                ticker.history,
                start=start_date,
                end=end_date,
                interval=interval,
            )
            
            if hist.empty:
                # Empty DataFrame usually indicates rate limiting or invalid symbol
                # Don't make additional requests - assume rate limit for safety
                raise DataUnavailableError(
                    f"No historical data for {symbol}. This may be due to rate limiting. "
                    "Please wait 60 seconds and try again.",
                    "yahoo"
                )
            
            results = []
            for idx, row in hist.iterrows():
                results.append(
                    PriceData(
                        symbol=symbol.upper(),
                        date=idx.date(),
                        open=Decimal(str(row["Open"])),
                        high=Decimal(str(row["High"])),
                        low=Decimal(str(row["Low"])),
                        close=Decimal(str(row["Close"])),
                        volume=int(row["Volume"]),
                        adjusted_close=None,
                        source="yahoo",
                        timestamp=datetime.now(timezone.utc),
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
            ticker = yf.Ticker(symbol, session=self._session)
            info = await asyncio.to_thread(lambda: ticker.info)
            
            if not info or 'symbol' not in info:
                raise SymbolNotFoundError(symbol, "yahoo")
            
            return FundamentalsData(
                symbol=symbol.upper(),
                company_name=info.get("longName"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=Decimal(str(info["marketCap"])) if "marketCap" in info else None,
                pe_ratio=Decimal(str(info["trailingPE"])) if "trailingPE" in info else None,
                eps=Decimal(str(info["trailingEps"])) if "trailingEps" in info else None,
                dividend_yield=Decimal(str(info["dividendYield"])) if "dividendYield" in info else None,
                beta=Decimal(str(info["beta"])) if "beta" in info else None,
                fifty_two_week_high=Decimal(str(info["fiftyTwoWeekHigh"])) if "fiftyTwoWeekHigh" in info else None,
                fifty_two_week_low=Decimal(str(info["fiftyTwoWeekLow"])) if "fiftyTwoWeekLow" in info else None,
                average_volume=info.get("averageVolume"),
                source="yahoo",
                timestamp=datetime.now(timezone.utc),
            )
            
        except (RateLimitExceededError, SymbolNotFoundError):
            raise
        except Exception as e:
            error_str = str(e).lower()
            if '429' in error_str or 'too many' in error_str:
                raise RateLimitExceededError("yahoo", retry_after=60)
            raise DataUnavailableError(f"Failed to fetch fundamentals: {e}", "yahoo")
    
    async def search_symbol(self, query: str) -> List[dict]:
        """Search symbols (limited to avoid rate limits)."""
        await self._wait_for_rate_limit()
        
        # Simplified search - just validate if it's a real symbol
        try:
            ticker = yf.Ticker(query.upper(), session=self._session)
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
