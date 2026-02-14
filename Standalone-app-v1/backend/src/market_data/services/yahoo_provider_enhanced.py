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
import pandas as pd
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
        self._primed = False
        
        # Create session with custom headers and retry logic
        self._session = self._create_session()
    
    def _create_session(self) -> Session:
        """Create a requests session with optimal settings for 2026."""
        session = Session()
        
        # Modern User-Agent (Chrome 132 style for 2026)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        })
        
        # Configure retry strategy with exponential backoff for 429
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    async def _prime_session(self):
        """Hit Yahoo Finance homepage to get necessary cookies and crumbs."""
        if self._primed:
            return
            
        try:
            # Hit homepage to establish session and cookies (B cookie, Crumb)
            await asyncio.to_thread(
                self._session.get, 
                "https://finance.yahoo.com", 
                timeout=10
            )
            self._primed = True
        except Exception as e:
            # Non-critical, yfinance might still work, but log it
            print(f"Warning: Failed to prime Yahoo session: {e}")
    
    async def _wait_for_rate_limit(self):
        """Enforce minimum delay between requests and ensure session is primed."""
        await self._prime_session()
        
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
                period="5day",
                interval="1d",
                auto_adjust=True, # Recommended for yf 1.x
            )
            
            if hist.empty:
                # In 1.1.0+, empty might mean valid symbol but blocked, or invalid symbol
                # Check ticker.info to verify symbol existence if possible
                info = await asyncio.to_thread(lambda: ticker.info)
                if not info or 'symbol' not in info:
                    raise SymbolNotFoundError(symbol, "yahoo")
                    
                raise DataUnavailableError(
                    f"No price data available for {symbol}. This may be due to rate limiting. "
                    "Session is now primed, please retry in 5 seconds.",
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
                return Decimal(str(last_row[col_name])) if col_name else Decimal(str(default))

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
                auto_adjust=True, # Recommended for yf 1.x
            )
            
            if hist.empty:
                # In 1.1.0+, empty might mean valid symbol but blocked
                raise DataUnavailableError(
                    f"No historical data for {symbol}. This may be due to rate limiting or invalid date range. "
                    "Session is now primed, please retry in 5 seconds.",
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
                    return Decimal(str(row[col_name])) if col_name else Decimal(str(default))

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
                    timestamp=datetime.now(timezone.utc),
                )
            
            def get_decimal_val(key):
                val = info.get(key)
                if val is None or val == "":
                    return None
                try:
                    return Decimal(str(val))
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
