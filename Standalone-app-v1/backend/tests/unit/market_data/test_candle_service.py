
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from src.market_data.candle_service import backfill_candles_on_startup

@pytest.mark.asyncio
async def test_backfill_candles_on_startup_upsert():
    from src.estimates.domain.entities import Estimate, EstimateStatus
    from src.market_data.domain.entities import Ticker
    
    mock_ticker = Ticker(id=1, symbol='AAPL')
    mock_est = Estimate(id=1, ticker_id=1, status=EstimateStatus.OPEN, target_price=160.0, stop_loss_price=140.0, start_price=150.0)
    mock_est.ticker = mock_ticker
    
    now = datetime.now()
    past_3_days = now - timedelta(days=3)
    
    # Mock data array
    mock_candles_data = [
        {'timestamp': past_3_days + timedelta(days=1), 'open': 150.0, 'high': 155.0, 'low': 145.0, 'close': 153.0, 'volume': 100},
        {'timestamp': past_3_days + timedelta(days=2), 'open': 153.0, 'high': 161.0, 'low': 150.0, 'close': 160.5, 'volume': 200}, # hits target!
    ]
    
    with patch('src.market_data.candle_service.AsyncSessionLocal') as mock_session_local, \
         patch('src.market_data.candle_service._fetch_yahoo_v8_candles', new_callable=AsyncMock) as mock_fetch, \
         patch('src.market_data.candle_service.sse_manager.broadcast', new_callable=AsyncMock) as mock_broadcast:
         
         mock_session = AsyncMock()
         mock_session_local.return_value.__aenter__.return_value = mock_session
         
         # Mock setup for queries
         mock_scalar_result = MagicMock()
         mock_scalar_result.scalars.return_value.all.return_value = [mock_est]
         
         # For second pass querying timestamps and candles
         mock_time_result = MagicMock()
         mock_time_result.scalar.return_value = past_3_days
         
         # We pretend there are no candles initially (exists_run.scalar_one_or_none returns None)
         mock_exists_run = MagicMock()
         mock_exists_run.scalar_one_or_none.return_value = None
         
         # mock_session.execute needs to return differently based on the order of calls
         # Call 1: active estimates
         # Call 2: max timestamp
         # Call 3: exists candle 1
         # Call 4: exists candle 2
         mock_session.execute.side_effect = [mock_scalar_result, mock_time_result, mock_exists_run, mock_exists_run]
         
         # return estimates from session.get
         mock_session.get.return_value = mock_est
         
         mock_fetch.return_value = mock_candles_data
         
         await backfill_candles_on_startup()
         
         # Assert target hit
         assert mock_est.status == EstimateStatus.CLOSED_WIN
         assert mock_est.exit_price == 160.0
         assert mock_session.add.call_count == 2 # 2 new candles added
         
         # check broadcasts
         assert mock_broadcast.call_count == 2
         # first broadcast should be estimate_update CLOSED_WIN
         assert mock_broadcast.call_args_list[0][0][0]['new_state'] == 'CLOSED_WIN'
         # second broadcast should be backfill_complete
         assert mock_broadcast.call_args_list[1][0][0]['type'] == 'backfill_complete'
         assert mock_broadcast.call_args_list[1][0][0]['candles_added'] == 2
         assert mock_broadcast.call_args_list[1][0][0]['state_changed'] == True

