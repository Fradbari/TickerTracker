"""
Finnhub Market Data Provider implementation (Stub).

Placeholder for future Finnhub integration.
"""

from datetime import date
from decimal import Decimal
from typing import List

from src.market_data.domain.providers import (
    MarketDataProvider,
    PriceData,
    FundamentalsData,
)


class FinnhubMarketDataProvider(MarketDataProvider):
    """
    Finnhub data provider implementation (Stub).
    
    This class exists to demonstrate the swappable provider architecture.
    Implementation will be added in a future phase.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_current_price(self, symbol: str) -> PriceData:
        raise NotImplementedError("Finnhub provider not yet implemented")
    
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        interval: str = "1d",
    ) -> List[PriceData]:
        raise NotImplementedError("Finnhub provider not yet implemented")
    
    async def get_fundamentals(self, symbol: str) -> FundamentalsData:
        raise NotImplementedError("Finnhub provider not yet implemented")
    
    async def search_symbol(self, query: str) -> List[dict]:
        raise NotImplementedError("Finnhub provider not yet implemented")
    
    @property
    def source_name(self) -> str:
        return "finnhub"
    
    @property
    def supports_realtime(self) -> bool:
        return True
