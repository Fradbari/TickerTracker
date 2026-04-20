
import pytest
from unittest.mock import AsyncMock, patch
from src.market_data.finnhub_client import symbol_lookup
from src.market_data.yahoo_client import validate_symbol_on_yahoo
from src.market_data.schemas.search import FinnhubSymbolResult, SymbolValidationResult

@pytest.mark.asyncio
async def test_symbol_lookup_filters_non_stock():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'count': 2,
            'result': [
                {'symbol': 'AAPL', 'description': 'Apple Inc', 'type': 'Common Stock', 'mic': 'XNAS'},
                {'symbol': 'BTCUSD', 'description': 'Bitcoin', 'type': 'Crypto', 'mic': 'CRYP'}
            ]
        }
        mock_get.return_value = mock_response
        
        results = await symbol_lookup('AAPL')
        
        assert len(results) == 1
        assert results[0].symbol == 'AAPL'
        assert results[0].type == 'Common Stock'

@pytest.mark.asyncio
async def test_symbol_lookup_exact_match_bypass():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'count': 1,
            'result': [
                {'symbol': 'MYCRYPTO', 'description': 'Custom Crypto', 'type': 'Crypto', 'mic': 'CRYP'}
            ]
        }
        mock_get.return_value = mock_response
        
        results = await symbol_lookup('mycrypto')
        
        assert len(results) == 1
        assert results[0].symbol == 'MYCRYPTO'

@pytest.mark.asyncio
async def test_validate_symbol_yahoo_200():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'chart': {
                'result': [
                    {'meta': {'regularMarketPrice': 150.5, 'currency': 'USD', 'exchangeName': 'NMS'}}
                ]
            }
        }
        mock_get.return_value = mock_response
        
        res = await validate_symbol_on_yahoo('AAPL')
        
        assert res.valid is True
        assert res.current_price == 150.5
        assert res.currency == 'USD'
        assert res.exchange == 'NMS'
        assert res.symbol == 'AAPL'

@pytest.mark.asyncio
async def test_validate_symbol_yahoo_404():
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        res = await validate_symbol_on_yahoo('INVLD')
        
        assert res.valid is False
        assert res.current_price is None

@pytest.mark.asyncio
async def test_symbol_search_endpoint_returns_max_8():
    from src.market_data.api.routes import advanced_symbol_search
    
    mock_finnhub = [FinnhubSymbolResult(symbol=f'SYM{i}', description='Desc', type='Common Stock') for i in range(12)]
    
    with patch('src.market_data.api.routes.symbol_lookup', return_value=mock_finnhub), \
         patch('src.market_data.api.routes.validate_symbol_on_yahoo', side_effect=lambda x: SymbolValidationResult(valid=True, symbol=x, current_price=10.0)), \
         patch('src.market_data.api.routes.get_redis', side_effect=Exception('No redis')):
         
        class DummyResponse:
            headers = {}
            
        res = await advanced_symbol_search(DummyResponse(), 'SYM')
        
        assert len(res.data) == 8


