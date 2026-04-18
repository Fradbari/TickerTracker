import pytest
import asyncio
from unittest.mock import patch
from src.market_data.services.yahoo_service import YahooFinanceService

@pytest.mark.chaos
@pytest.mark.asyncio
async def test_yahoo_finance_timeout_fallback_to_cache(test_app, monkeypatch):
    """
    Simula un Timeout assoluto verso le API di Yahoo Finance durante la 
    richiesta LivePrices: il sistema deve loggare l'errore o continuare 
    utilizzando vecchi dati in cache (senza che il task muoia).
    """
    
    # 2. Forziamo YahooService a far scattare Exception di Timeout
    async def mock_timeout_fetch(*args, **kwargs):
        raise TimeoutError("Simulated Yahoo Timeout (Chaos Engine)")
        
    with patch("src.market_data.services.yahoo_service.YahooFinanceService._fetch_from_api", side_effect=mock_timeout_fetch):
        # 3. Esegui il fetch per il Task 3B logic
        result = await YahooFinanceService.get_live_prices(["AAPL"])
        
    # 4. Validiamo asserzioni
    # App non deve crashare. Result deve essere coerente con i dati cached old (o vuoto/graceful degradation)
    assert result is not None, "Il loop background è fallito silenziosamente in timeout"
