"""
Schemas for MarketData operations.

Provides input/output types for repository methods.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class MarketDataRow(BaseModel):
    """
    Input schema for upserting market data.

    Used in upsert_daily() to provide OHLCV data for a single trading day.

    Attributes:
        date: Trading date
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        data_source: Source of the data (default: 'yahoo')
        quality_score: Quality score 0.00-1.00 (default: 0.80)
    """

    date: date = Field(description="Trading date")
    open: Decimal = Field(gt=0, description="Opening price")
    high: Decimal = Field(gt=0, description="Highest price")
    low: Decimal = Field(gt=0, description="Lowest price")
    close: Decimal = Field(gt=0, description="Closing price")
    volume: int = Field(ge=0, description="Trading volume")
    data_source: str = Field(default="yahoo", max_length=50, description="Data source")
    quality_score: Decimal | None = Field(
        default=Decimal("0.80"),
        ge=0,
        le=1,
        description="Quality score 0.00-1.00"
    )

    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v, info):
        """Validate that high >= low, open, close."""
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('high must be >= low')
        if 'open' in info.data and v < info.data['open']:
            raise ValueError('high must be >= open')
        if 'close' in info.data and v < info.data['close']:
            raise ValueError('high must be >= close')
        return v

    @field_validator('low')
    @classmethod
    def low_must_be_lowest(cls, v, info):
        """Validate that low <= open, close."""
        if 'open' in info.data and v > info.data['open']:
            raise ValueError('low must be <= open')
        if 'close' in info.data and v > info.data['close']:
            raise ValueError('low must be <= close')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-02-08",
                "open": "150.25",
                "high": "152.75",
                "low": "149.50",
                "close": "151.80",
                "volume": 1250000,
                "data_source": "yahoo",
                "quality_score": "0.85"
            }
        }


class AggregatedData(BaseModel):
    """
    Output schema for aggregated market data.

    Used by get_aggregated() to return aggregated OHLCV data over intervals.

    Attributes:
        period_start: Start date of the aggregation period
        period_end: End date of the aggregation period
        interval: Aggregation interval ("1D", "1W", "1M")
        open: Opening price (first day's open)
        high: Highest price in period
        low: Lowest price in period
        close: Closing price (last day's close)
        volume: Total volume in period
        avg_close: Average closing price
        days_count: Number of trading days in period
    """

    period_start: date = Field(description="Period start date")
    period_end: date = Field(description="Period end date")
    interval: str = Field(description="Aggregation interval")

    open: Decimal = Field(description="Opening price (first day)")
    high: Decimal = Field(description="Highest price in period")
    low: Decimal = Field(description="Lowest price in period")
    close: Decimal = Field(description="Closing price (last day)")
    volume: int = Field(description="Total volume in period")

    avg_close: Decimal = Field(description="Average closing price")
    days_count: int = Field(description="Number of trading days")

    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2026-02-01",
                "period_end": "2026-02-07",
                "interval": "1W",
                "open": "148.50",
                "high": "153.25",
                "low": "147.80",
                "close": "151.90",
                "volume": 6250000,
                "avg_close": "150.75",
                "days_count": 5
            }
        }
