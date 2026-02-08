"""
Filter schemas for MarketData queries.

Provides type-safe filtering options for MarketDataRepository.
"""

from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MarketDataFilters(BaseModel):
    """
    Filters for querying MarketData entities.
    
    All filters are optional and combined with AND logic.
    
    Attributes:
        ticker_id: Filter by specific ticker (optional due to range queries)
        start_date: Query data from this date onwards (inclusive)
        end_date: Query data up to this date (inclusive)
        min_quality_score: Minimum data quality score (0.0 - 1.0)
        data_source: Filter by data source (default: "yahoo")
    """
    
    ticker_id: Optional[UUID] = Field(default=None, description="Filter by ticker ID")
    start_date: Optional[date] = Field(default=None, description="Start date (inclusive)")
    end_date: Optional[date] = Field(default=None, description="End date (inclusive)")
    min_quality_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum quality score filter"
    )
    data_source: Optional[str] = Field(default=None, description="Data source filter (e.g., 'yahoo')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "min_quality_score": 0.8,
                "data_source": "yahoo"
            }
        }
    
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.ticker_id is not None,
            self.start_date is not None,
            self.end_date is not None,
            self.min_quality_score is not None,
            self.data_source is not None,
        ])


class MarketDataAggregationParams(BaseModel):
    """
    Parameters for aggregating MarketData into time periods.
    
    Attributes:
        interval: Aggregation interval ("1D", "1W", "1M")
        start_date: Start date for aggregation (optional)
        end_date: End date for aggregation (optional)
    """
    
    interval: str = Field(
        default="1W",
        description="Aggregation interval (1D=daily, 1W=weekly, 1M=monthly)"
    )
    start_date: Optional[date] = Field(default=None, description="Start date for aggregation")
    end_date: Optional[date] = Field(default=None, description="End date for aggregation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "interval": "1W",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }
