import pytest
from unittest.mock import AsyncMock, patch
import json
from fastapi import HTTPException
from src.shared.api.admin_routes import save_finnhub_key, FinnhubKeyRequest, get_finnhub_key
from src.shared.domain.app_config import AppConfig

@pytest.mark.asyncio
async def test_save_finnhub_key_success():
    req = FinnhubKeyRequest(api_key="valid_key")
    db_mock = AsyncMock()
    
    db_mock.execute.return_value.scalar_one_or_none.return_value = None
    
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.headers = {"X-Ratelimit-Limit": "60"}
        mock_get.return_value = mock_response
        
        result = await save_finnhub_key(req, db=db_mock)
        assert result["valid"] is True
        assert result["quota_remaining"] == "60"
        assert db_mock.add.called
        assert db_mock.commit.called

@pytest.mark.asyncio
async def test_save_finnhub_key_failure():
    req = FinnhubKeyRequest(api_key="invalid_key")
    db_mock = AsyncMock()
    
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        try:
            await save_finnhub_key(req, db=db_mock)
        except Exception as e:
            assert type(e) is HTTPException
            assert e.status_code == 400
