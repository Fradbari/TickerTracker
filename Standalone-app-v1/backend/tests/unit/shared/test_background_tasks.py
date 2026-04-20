import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from src.shared.background_tasks import start_price_loop
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.domain.entities import Ticker

@pytest.fixture
def mock_open_estimates():
    ticker1 = Ticker(id=1, symbol="AAPL")
    est1 = Estimate(id=101, ticker_id=1, status=EstimateStatus.OPEN, is_deleted=False, 
                    start_price=100.0, target_price=150.0, stop_loss_price=80.0)
    est1.ticker = ticker1
    
    ticker2 = Ticker(id=2, symbol="MSFT")
    est2 = Estimate(id=102, ticker_id=2, status=EstimateStatus.OPEN, is_deleted=False, 
                    start_price=200.0, target_price=250.0, stop_loss_price=180.0)
    est2.ticker = ticker2
    
    return [est1, est2]

@pytest.fixture
def mock_db_session(mock_open_estimates):
    class MockInnerSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def get(self, entity, id):
            for e in mock_open_estimates:
                if e.id == id:
                    return e
            return None
        async def commit(self):
            pass

    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def execute(self, stmt):
            mock_result = MagicMock()
            mock_result.scalars().all.return_value = mock_open_estimates
            return mock_result
            
    mock_factory = MagicMock()
    mock_factory.return_value = MockSession()
    # Replace AsyncSessionLocal locally to return different sessions based on whether inner or outer calls
    # but unittest.mock makes it tricky since they share the same class. We can wrap it nicely if needed.
    
    return mock_factory

@pytest.mark.asyncio
async def test_price_loop_closes_estimate_on_tp(mock_open_estimates, mocker):
    mocker.patch("src.shared.background_tasks.get_settings", return_value=MagicMock(PRICE_LOOP_INTERVAL_SECONDS=0.01))
    
    # Mocking Database
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = mock_open_estimates
    
    mock_session_instance = AsyncMock()
    mock_session_instance.execute.return_value = mock_result
    
    async def mock_get(entity, id):
        for e in mock_open_estimates:
            if e.id == id:
                return e
        return None
        
    mock_session_instance.get.side_effect = mock_get
    
    mock_session_class = mocker.patch("src.shared.background_tasks.AsyncSessionLocal")
    mock_session_class.return_value.__aenter__.return_value = mock_session_instance
    
    # Mock Yahoo price
    async def mock_yahoo_price(symbol):
        if symbol == "AAPL":
            return 155.0 # >= target_price (150.0) -> should close win
        return 220.0 # no hit for MSFT
        
    mocker.patch("src.shared.background_tasks.get_current_price", side_effect=mock_yahoo_price)
    mock_finnhub = mocker.patch("src.shared.background_tasks.get_quote")
    
    # Mock SSE
    mock_sse = mocker.patch("src.shared.background_tasks.sse_manager.broadcast", new_callable=AsyncMock)
    
    # Mock sleep to raise CancelledError after first iteration to exit loop
    mock_sleep = mocker.patch("asyncio.sleep", side_effect=asyncio.CancelledError)
    
    await start_price_loop({})
    
    assert mock_open_estimates[0].status == EstimateStatus.CLOSED_WIN
    assert mock_open_estimates[0].exit_price == 150.0
    assert mock_open_estimates[0].realized_pnl == 50.0
    
    assert mock_open_estimates[1].status == EstimateStatus.OPEN
    
    mock_finnhub.assert_not_called()
    mock_sse.assert_called_once()
    
    assert mock_session_instance.commit.call_count >= 1

@pytest.mark.asyncio
async def test_price_loop_fallback_to_finnhub(mock_open_estimates, mocker):
    mocker.patch("src.shared.background_tasks.get_settings", return_value=MagicMock(PRICE_LOOP_INTERVAL_SECONDS=0.01))
    
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_open_estimates[0]]
    
    mock_session_instance = AsyncMock()
    mock_session_instance.execute.return_value = mock_result
    
    async def mock_get(entity, id):
        if id == mock_open_estimates[0].id: return mock_open_estimates[0]
        return None
        
    mock_session_instance.get.side_effect = mock_get
    
    mocker.patch("src.shared.background_tasks.AsyncSessionLocal").return_value.__aenter__.return_value = mock_session_instance
    
    # Yahoo fails (None), Finnhub hits SL
    mocker.patch("src.shared.background_tasks.get_current_price", return_value=None)
    mocker.patch("src.shared.background_tasks.get_quote", return_value={"c": 75.0, "h": 90.0, "l": 70.0}) # 75.0 <= SL (80.0) -> hit
    
    mock_sse = mocker.patch("src.shared.background_tasks.sse_manager.broadcast", new_callable=AsyncMock)
    mocker.patch("asyncio.sleep", side_effect=asyncio.CancelledError)
    
    await start_price_loop({})
    
    assert mock_open_estimates[0].status == EstimateStatus.CLOSED_LOSS
    assert mock_open_estimates[0].exit_price == 80.0
    assert mock_open_estimates[0].realized_pnl == -20.0
    mock_sse.assert_called_once()

@pytest.mark.asyncio
async def test_price_loop_handles_single_ticker_error(mock_open_estimates, mocker):
    mocker.patch("src.shared.background_tasks.get_settings", return_value=MagicMock(PRICE_LOOP_INTERVAL_SECONDS=0.01))
    
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = mock_open_estimates
    
    mock_session_instance = AsyncMock()
    mock_session_instance.execute.return_value = mock_result
    async def mock_get(entity, id):
        for e in mock_open_estimates:
            if e.id == id: return e
        return None
    mock_session_instance.get.side_effect = mock_get
    mocker.patch("src.shared.background_tasks.AsyncSessionLocal").return_value.__aenter__.return_value = mock_session_instance
    
    # AAPL raises Exception, MSFT succeeds and hits target
    async def mock_yahoo_price(symbol):
        if symbol == "AAPL":
            raise ValueError("API Offline")
        return 260.0 # hit for MSFT
        
    mocker.patch("src.shared.background_tasks.get_current_price", side_effect=mock_yahoo_price)
    mock_sse = mocker.patch("src.shared.background_tasks.sse_manager.broadcast", new_callable=AsyncMock)
    mocker.patch("asyncio.sleep", side_effect=asyncio.CancelledError)
    
    await start_price_loop({})
    
    # AAPL should still be OPEN
    assert mock_open_estimates[0].status == EstimateStatus.OPEN
    # MSFT should be CLOSED_WIN
    assert mock_open_estimates[1].status == EstimateStatus.CLOSED_WIN
    assert mock_open_estimates[1].exit_price == 250.0
    
    mock_sse.assert_called_once()

@pytest.mark.asyncio
async def test_price_loop_cancelled_gracefully(mocker):
    mocker.patch("src.shared.background_tasks.get_settings", return_value=MagicMock(PRICE_LOOP_INTERVAL_SECONDS=0.01))
    # It will raise CancelledError immediately on DB query
    mocker.patch("src.shared.background_tasks.AsyncSessionLocal", side_effect=asyncio.CancelledError)
    
    # Should exit cleanly without raising an unhandled exception
    await start_price_loop({})
