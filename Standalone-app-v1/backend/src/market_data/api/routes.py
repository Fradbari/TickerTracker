"""
Market Data API Routes (TASK 2.17)

Exposes REST endpoints for:
- Current price data
- Historical price data with aggregation
- Fundamental data
- Symbol search/autocomplete

All endpoints use MarketDataProvider (TASK 2.18-2.19) for data retrieval.
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

from src.market_data.domain.providers import (
    MarketDataProvider,
    PriceData,
    FundamentalsData,
    SymbolNotFoundError,
    DataUnavailableError,
)
from src.market_data.api.dependencies import get_market_data_provider
from src.market_data.schemas.lineage import MarketDataLineageSchema
from src.shared.schemas.api_response import ApiResponse
from src.infra.security.rate_limit import limiter, is_whitelisted


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class PriceResponse(BaseModel):
    """Response schema for current price endpoint."""
    symbol: str
    price: str  # Decimal as string for JSON
    open: str
    high: str
    low: str
    close: str
    volume: int
    date: date
    source: str
    timestamp: datetime
    is_stale: bool = Field(False, description="Whether data is from stale cache")


class HistoricalPricePoint(BaseModel):
    """Single historical price data point."""
    date: date
    open: str
    high: str
    low: str
    close: str
    volume: int
    lineage: Optional[MarketDataLineageSchema] = Field(
        None, description="Data lineage metadata (present when ?include_lineage=true)"
    )


class HistoryResponse(BaseModel):
    """Response schema for historical prices endpoint."""
    symbol: str
    interval: str
    start_date: date
    end_date: date
    data: List[HistoricalPricePoint]
    source: str
    timestamp: datetime


class FundamentalsResponse(BaseModel):
    """Response schema for fundamentals endpoint."""
    symbol: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[str] = None
    pe_ratio: Optional[str] = None
    eps: Optional[str] = None
    dividend_yield: Optional[str] = None
    beta: Optional[str] = None
    fifty_two_week_high: Optional[str] = None
    fifty_two_week_low: Optional[str] = None
    average_volume: Optional[int] = None
    source: str
    timestamp: datetime
    is_stale: bool = False


class SearchResult(BaseModel):
    """Single search result."""
    symbol: str
    name: str
    exchange: Optional[str] = None


class SearchResponse(BaseModel):
    """Response schema for symbol search endpoint."""
    query: str
    results: List[SearchResult]
    count: int


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api/market", tags=["Market Data"])


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/price/{ticker}",
    response_model=ApiResponse[PriceResponse],
    summary="Get current price for a ticker",
    description="Returns the most recent price data for the specified ticker symbol. "
                "Includes OHLCV data and metadata (source, timestamp, stale flag)."
)
@limiter.limit("60/minute", exempt_when=is_whitelisted)
async def get_current_price(
    request: Request,
    ticker: str,
    response: Response,
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """
    Get current/most recent price for a ticker symbol.
    
    **Cache-Control**: Data is cached for 1 hour (3600 seconds).
    """
    try:
        price_data: PriceData = await provider.get_current_price(ticker.upper())
        
        # Set cache headers
        cache_duration = 3600 if not price_data.is_stale else 60
        response.headers["Cache-Control"] = f"public, max-age={cache_duration}"
        
        price_response = PriceResponse(
            symbol=price_data.symbol,
            price=str(price_data.close),
            open=str(price_data.open),
            high=str(price_data.high),
            low=str(price_data.low),
            close=str(price_data.close),
            volume=price_data.volume,
            date=price_data.date,
            source=price_data.source,
            timestamp=price_data.timestamp,
            is_stale=price_data.is_stale,
        )
        
        return ApiResponse.success(
            data=price_response,
            message=f"Current price for {ticker.upper()}"
        )
        
    except SymbolNotFoundError:
        raise HTTPException(status_code=404, detail=f"Symbol '{ticker}' not found")
    except DataUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")


@router.get(
    "/history/{ticker}",
    response_model=ApiResponse[HistoryResponse],
    summary="Get historical price data",
    description="Returns historical OHLCV data for the specified ticker and date range. "
                "Supports aggregation intervals: 1d (daily), 1w (weekly), 1m (monthly)."
)
async def get_historical_prices(
    ticker: str,
    response: Response,
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
    interval: str = Query("1d", pattern="^(1d|1w|1m)$", description="Data interval"),
    include_lineage: bool = Query(False, description="Include data lineage metadata"),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """
    Get historical price data with optional aggregation.
    
    **Intervals**:
    - `1d`: Daily data (default)
    - `1w`: Weekly aggregated data
    - `1m`: Monthly aggregated data
    
    **Cache-Control**: Data is cached for 1 day (86400 seconds).
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before or equal to end_date"
            )
        
        price_history: List[PriceData] = await provider.get_historical_prices(
            symbol=ticker.upper(),
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
        
        # Set cache headers (historical data changes less frequently)
        response.headers["Cache-Control"] ="public, max-age=86400"
        
        history_points = [
            HistoricalPricePoint(
                date=p.date,
                open=str(p.open),
                high=str(p.high),
                low=str(p.low),
                close=str(p.close),
                volume=p.volume,
                lineage=MarketDataLineageSchema(
                    data_source=p.source,
                    source_timestamp=p.timestamp,
                    ingestion_timestamp=datetime.utcnow(),
                    quality_score=None,
                ) if include_lineage else None,
            )
            for p in price_history
        ]
        
        history_response = HistoryResponse(
            symbol=ticker.upper(),
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            data=history_points,
            source=price_history[0].source if price_history else "unknown",
            timestamp=datetime.utcnow(),
        )
        
        return ApiResponse.success(
            data=history_response,
            message=f"Historical data for {ticker.upper()} ({len(history_points)} points)"
        )
        
    except SymbolNotFoundError:
        raise HTTPException(status_code=404, detail=f"Symbol '{ticker}' not found")
    except DataUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


@router.get(
    "/fundamentals/{ticker}",
    response_model=ApiResponse[FundamentalsResponse],
    summary="Get fundamental data",
    description="Returns fundamental/company data for the specified ticker. "
                "Includes metrics like P/E ratio, market cap, dividend yield, etc."
)
async def get_fundamentals(
    ticker: str,
    response: Response,
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """
    Get fundamental data for a ticker symbol.
    
    Returns financial metrics and company information.
    Not all fields may be available from all data sources.
    
    **Cache-Control**: Data is cached for 1 day (86400 seconds).
    """
    try:
        fundamentals: FundamentalsData = await provider.get_fundamentals(ticker.upper())
        
        # Set cache headers (fundamentals change infrequently)
        response.headers["Cache-Control"] = "public, max-age=86400"
        
        fundamentals_response = FundamentalsResponse(
            symbol=fundamentals.symbol,
            company_name=fundamentals.company_name,
            sector=fundamentals.sector,
            industry=fundamentals.industry,
            market_cap=str(fundamentals.market_cap) if fundamentals.market_cap else None,
            pe_ratio=str(fundamentals.pe_ratio) if fundamentals.pe_ratio else None,
            eps=str(fundamentals.eps) if fundamentals.eps else None,
            dividend_yield=str(fundamentals.dividend_yield) if fundamentals.dividend_yield else None,
            beta=str(fundamentals.beta) if fundamentals.beta else None,
            fifty_two_week_high=str(fundamentals.fifty_two_week_high) if fundamentals.fifty_two_week_high else None,
            fifty_two_week_low=str(fundamentals.fifty_two_week_low) if fundamentals.fifty_two_week_low else None,
            average_volume=fundamentals.average_volume,
            source=fundamentals.source,
            timestamp=fundamentals.timestamp,
            is_stale=fundamentals.is_stale,
        )
        
        return ApiResponse.success(
            data=fundamentals_response,
            message=f"Fundamentals for {ticker.upper()}"
        )
        
    except SymbolNotFoundError:
        raise HTTPException(status_code=404, detail=f"Symbol '{ticker}' not found")
    except DataUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fundamentals: {str(e)}")


@router.get(
    "/search",
    response_model=ApiResponse[SearchResponse],
    summary="Search for ticker symbols",
    description="Search for ticker symbols by company name or symbol fragment. "
                "Returns up to 10 results ordered by relevance."
)
async def search_symbols(
    response: Response,
    q: str = Query(..., min_length=1, description="Search query"),
    provider: MarketDataProvider = Depends(get_market_data_provider),
):
    """
    Search for ticker symbols (autocomplete).
    
    Useful for symbol discovery and autocomplete features.
    Returns max 10 results ordered by relevance.
    
    **Cache-Control**: Search results are cached for 1 hour.
    """
    try:
        search_results = await provider.search_symbol(q)
        
        # Limit to 10 results, ordered by relevance (provider should handle this)
        limited_results = search_results[:10]
        
        # Set cache headers
        response.headers["Cache-Control"] = "public, max-age=3600"
        
        results = [
            SearchResult(
                symbol=r.get("symbol", ""),
                name=r.get("name", ""),
                exchange=r.get("exchange"),
            )
            for r in limited_results
        ]
        
        search_response = SearchResponse(
            query=q,
            results=results,
            count=len(results),
        )
        
        return ApiResponse.success(
            data=search_response,
            message=f"Found {len(results)} results for '{q}'"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching symbols: {str(e)}")