"""
Lineage Schemas — TASK 3.9

Pydantic schemas for exposing data-lineage metadata through the REST API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MarketDataLineageSchema(BaseModel):
    """
    Lineage metadata optionally returned alongside OHLCV data.

    Included in API responses when the query parameter
    ``?include_lineage=true`` is passed to any endpoint that returns
    OHLCV data (e.g. ``GET /api/market/history/{ticker}``).

    Attributes:
        data_source:          Source identifier (DataSource enum value).
        source_timestamp:     When data was generated at the source.
        ingestion_timestamp:  When data entered our system.
        quality_score:        Quality score 0.00–1.00; ``None`` if not computed.
    """

    data_source: str = Field(description="Data source identifier (e.g. 'yahoo_finance')")
    source_timestamp: Optional[datetime] = Field(
        None, description="UTC timestamp when data was generated at the source"
    )
    ingestion_timestamp: datetime = Field(
        description="UTC timestamp when data was ingested into the system"
    )
    quality_score: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Data quality score 0.00–1.00",
    )

    model_config = {"from_attributes": True}
