class YahooFinanceService:
    @staticmethod
    async def get_live_prices(symbols: list[str]) -> dict:
        # Mock logic
        return {s: 100.0 for s in symbols}

    @staticmethod
    async def _fetch_from_api(symbol: str) -> dict:
        return {}
