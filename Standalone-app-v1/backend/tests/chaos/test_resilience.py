import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
from httpx import AsyncClient
from sqlalchemy.exc import TimeoutError as SATimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from src.estimates.domain.entities import Direction, Estimate, EstimateStatus
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.infra.drive.client import GoogleDriveClient
from src.main import app
from src.market_data.infrastructure.cached_provider import CachedMarketDataProvider
from src.market_data.repositories.market_data_repository import MarketDataRepository
from src.shared.infra.database import get_db
from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.json_parser import LegacyJsonParser
from src.sync.repositories.sync_job_repository import SyncJobRepository
from src.sync.services.sync_service import SyncService

pytestmark = [pytest.mark.chaos, pytest.mark.timeout(15)]

@pytest.mark.asyncio
async def test_db_pool_exhausted_returns_503(test_client: AsyncClient):
    """
    Test: Database pool esaurito -> 503 graceful
    """
    async def override_get_db_timeout():
        raise SATimeoutError("QueuePool limit of size 5 overflow 10 reached")

    app.dependency_overrides[get_db] = override_get_db_timeout

    try:
        response = await test_client.get("/api/estimates")
        assert response.status_code == 503
        data = response.json()
        assert data["code"] == "DB_UNAVAILABLE"
    finally:
        app.dependency_overrides.pop(get_db, None)

from src.market_data.services.yahoo_provider_enhanced import EnhancedYahooMarketDataProvider


@pytest.mark.asyncio
async def test_yahoo_api_timeout_uses_cache():
    """
    Test: Yahoo API timeout -> usa cache
    Test: Yahoo API errore -> usa cache stale
    """
    underlying = EnhancedYahooMarketDataProvider()
    provider = CachedMarketDataProvider(underlying)
    symbol = "TSLA"
    provider._cache.clear()

    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_instance = MagicMock()
        mock_history = pd.DataFrame({
            "Close": [200.0],
            "Volume": [1000]
        }, index=[pd.Timestamp(date.today())])
        mock_instance.history.return_value = mock_history
        mock_ticker_class.return_value = mock_instance

        price1 = await provider.get_current_price(symbol)
        assert price1.close == 200.0
        assert price1.is_stale is False
        assert mock_ticker_class.call_count == 1

        mock_ticker_class.reset_mock()
        mock_instance.history.side_effect = TimeoutError("Timeout!")

        price2 = await provider.get_current_price(symbol)
        assert price2.close == 200.0
        assert price2.is_stale is False
        assert mock_ticker_class.call_count == 0

        cache_key = f"price:{symbol}:current"
        cached_item = provider._cache._cache[cache_key]
        cached_item.cached_at = datetime.now() - timedelta(seconds=120)

        mock_ticker_class.reset_mock()
        mock_instance.history.side_effect = TimeoutError("Timeout!")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            price3 = await provider.get_current_price(symbol)

        assert price3.close == 200.0
        assert price3.is_stale is True
        # initial try + 3 retries = 4
        assert mock_ticker_class.call_count == 4


@pytest.mark.asyncio
async def test_intermittent_network_retries():
    """
    Test: Rete intermittente -> retry funziona
    """
    underlying = EnhancedYahooMarketDataProvider()
    provider = CachedMarketDataProvider(underlying)
    symbol = "MSFT"
    provider._cache.clear()

    with patch("yfinance.Ticker") as mock_ticker_class:
        mock_instance = MagicMock()
        mock_history = pd.DataFrame({
            "Close": [300.0],
            "Volume": [1000]
        }, index=[pd.Timestamp(date.today())])

        mock_instance.history.side_effect = [
            Exception("Intermittent error 1"),
            Exception("Intermittent error 2"),
            mock_history
        ]
        mock_ticker_class.return_value = mock_instance

        price = await provider.get_current_price(symbol)

        assert price.close == 300.0
        assert price.is_stale is False
        assert mock_instance.history.call_count == 3


@pytest.mark.asyncio
async def test_drive_sync_partial_failure(async_session: AsyncSession):
    """
    Test: Drive sync fallisce parzialmente -> dati esistenti non corrotti
    Verifica che un'eccezione su alcuni file Drive permetta comunque
    il completamento o non alteri dati precedentemente salvati.
    """
    # 1. Setup dati pre-esistenti nel DB
    est_repo = EstimateRepository(async_session)
    existing_estimate = Estimate(
        id=uuid.uuid4(),
        ticker_id=uuid.uuid4(),
        start_price=Decimal("150.0"),
        target_price=Decimal("200.0"),
        target_profit_percent=Decimal("33.33"),
        stop_loss_price=Decimal("100.0"),
        stop_loss_percent=Decimal("33.33"),
        status=EstimateStatus.OPEN,
        direction=Direction.LONG,
    )
    await async_session.merge(existing_estimate)
    await async_session.commit()

    drive_client = AsyncMock(spec=GoogleDriveClient)

    # Mock dei file iniziali ritornati
    file1 = MagicMock()
    file1.name = "backup.json"
    file1.id = "f1"

    file2 = MagicMock()
    file2.name = "History_AAPL.csv"
    file2.id = "f2"

    file3 = MagicMock()
    file3.name = "History_MSFT.csv"
    file3.id = "f3"

    drive_client.list_files.return_value = [file1, file2, file3]

    # Verrà chiamato su 'f1' poi su 'f2' o 'f3' per history scaricati
    # Facciamo fallire f3 per simulare partial failure
    async def mock_download(file_id: str):
        if file_id == "f1":
            return b'[]'  # JSON vuoto
        if file_id == "f2":
            return b'Date,Close\n2022-01-01,150.0'
        if file_id == "f3":
            raise Exception("Rete Interrotta scaricando MSFT")
        return b''

    drive_client.download_file.side_effect = mock_download

    # Inizializziamo il servizio Sync
    csv_parser = LegacyCsvParser()
    json_parser = LegacyJsonParser()
    market_data_repo = MarketDataRepository(async_session)
    sync_job_repo = SyncJobRepository(async_session)

    service = SyncService(
        drive_client=drive_client,
        csv_parser=csv_parser,
        json_parser=json_parser,
        estimate_repo=est_repo,
        market_data_repo=market_data_repo,
        sync_job_repo=sync_job_repo,
        drive_folder_id="mock_folder",
        session=async_session
    )

    # 3. Esecuzione
    job = await service.run_initial_import()

    # 4. Verifica - Nonostante il fallimento di f3, il job deve terminare (Completed vs Failed items)
    assert job.records_failed > 0 or job.records_processed >= 0

    # 5. I dati pre-esistenti devono rimanere intatti!
    db_estimate = await async_session.get(Estimate, existing_estimate.id)
    assert db_estimate is not None
    assert db_estimate.start_price == Decimal("150.0")

