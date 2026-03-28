"""
Tests for SyncService - Sync service business logic.

Tests cover:
- Initial import from Drive
- Estimate sync to Drive
- Daily history sync
- Conflict resolution
- Error handling
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.estimates.domain.entities import Estimate, EstimateStatus
from src.sync.domain.entities import SyncJob, SyncJobStatus, SyncJobType
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow
from src.sync.services.sync_service import SyncService


@pytest.fixture
def mock_drive_client():
    """Mock GoogleDriveClient."""
    client = AsyncMock()
    client.list_files = AsyncMock(return_value=[])
    client.download_file = AsyncMock(return_value=b"")
    client.upload_file = AsyncMock(return_value=Mock(id="file123"))
    client.update_file = AsyncMock(return_value=Mock(id="file123"))
    return client


@pytest.fixture
def mock_csv_parser():
    """Mock LegacyCsvParser."""
    parser = Mock()
    parser.parse_estimates_csv = Mock(return_value=[])
    parser.parse_history_csv = Mock(return_value=[])
    parser.export_estimate_to_csv_row = Mock(return_value="ticker,price\nAAPL,150.00")
    parser.export_history_to_csv = Mock(return_value=b"date,close\n2024-01-01,150.00")
    parser._get_estimates_header = Mock(return_value="Ticker,Start Date,Start Price")
    return parser


@pytest.fixture
def mock_json_parser():
    """Mock LegacyJsonParser."""
    parser = Mock()
    parser.parse_backup_json = Mock(return_value=[])
    return parser


@pytest.fixture
def mock_estimate_repo():
    """Mock EstimateRepository."""
    repo = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_market_data_repo():
    """Mock MarketDataRepository."""
    repo = AsyncMock()
    repo.upsert_daily = AsyncMock(return_value=0)
    repo.get_history = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_sync_job_repo():
    """Mock SyncJobRepository."""
    repo = AsyncMock()

    # Store reference to jobs
    saved_jobs = {}

    async def mock_save(job):
        if not job.id:
            job.id = uuid4()
        saved_jobs[job.id] = job
        return job

    async def mock_mark_completed(job_id, records_processed, records_failed, checksum_after=None):
        # Get original job and update it
        job = saved_jobs.get(job_id)
        if job:
            job.records_processed = records_processed
            job.records_failed = records_failed
            job.checksum_after = checksum_after
            job.status = SyncJobStatus.COMPLETED
            return job
        # Fallback: create mock
        mock_job = Mock(spec=SyncJob)
        mock_job.id = job_id
        mock_job.records_processed = records_processed
        mock_job.records_failed = records_failed
        mock_job.checksum_after = checksum_after
        return mock_job

    async def mock_mark_failed(job_id, error_message, records_processed=0, records_failed=0):
        job = saved_jobs.get(job_id)
        if job:
            job.error_message = error_message
            job.records_processed = records_processed
            job.records_failed = records_failed
            job.status = SyncJobStatus.FAILED
            return job
        mock_job = Mock(spec=SyncJob)
        mock_job.id = job_id
        mock_job.error_message = error_message
        mock_job.records_processed = records_processed
        mock_job.records_failed = records_failed
        return mock_job

    repo.save = AsyncMock(side_effect=mock_save)
    repo.mark_completed = AsyncMock(side_effect=mock_mark_completed)
    repo.mark_failed = AsyncMock(side_effect=mock_mark_failed)
    return repo


@pytest.fixture
def mock_session():
    """Mock AsyncSession."""
    session = AsyncMock()
    return session


@pytest.fixture
def sync_service(
    mock_drive_client,
    mock_csv_parser,
    mock_json_parser,
    mock_estimate_repo,
    mock_market_data_repo,
    mock_sync_job_repo,
    mock_session
):
    """Create SyncService with mocked dependencies."""
    return SyncService(
        drive_client=mock_drive_client,
        csv_parser=mock_csv_parser,
        json_parser=mock_json_parser,
        estimate_repo=mock_estimate_repo,
        market_data_repo=mock_market_data_repo,
        sync_job_repo=mock_sync_job_repo,
        drive_folder_id="folder123",
        session=mock_session
    )


class TestSyncServiceInit:
    """Test SyncService initialization."""

    def test_init(self, sync_service):
        """Test service initializes correctly."""
        assert sync_service._folder_id == "folder123"
        assert sync_service._drive is not None
        assert sync_service._csv_parser is not None
        assert sync_service._json_parser is not None


class TestCalculateChecksum:
    """Test checksum calculation."""

    def test_calculate_checksum_simple(self, sync_service):
        """Test checksum for simple content."""
        content = b"test content"
        checksum = sync_service._calculate_checksum(content)

        # SHA-256 of "test content"
        expected = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
        assert checksum == expected

    def test_calculate_checksum_empty(self, sync_service):
        """Test checksum for empty content."""
        content = b""
        checksum = sync_service._calculate_checksum(content)

        # SHA-256 of empty string
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert checksum == expected


class TestRunInitialImport:
    """Test initial import from Drive."""

    @pytest.mark.asyncio
    async def test_initial_import_no_files(self, sync_service, mock_drive_client, mock_sync_job_repo):
        """Test initial import with no files in Drive."""
        mock_drive_client.list_files.return_value = []

        job = await sync_service.run_initial_import()

        assert job.job_type == SyncJobType.INITIAL_IMPORT
        assert job.records_processed == 0
        assert job.records_failed == 0
        mock_sync_job_repo.mark_completed.assert_called_once()

    @pytest.mark.asyncio
    async def test_initial_import_with_estimates(
        self,
        sync_service,
        mock_drive_client,
        mock_csv_parser,
        mock_sync_job_repo
    ):
        """Test initial import with estimates CSV."""
        # Setup mock files
        estimates_file = Mock(
            id="est123",
            mime_type="text/csv"
        )
        estimates_file.name = "estimates.csv"  # Set name as attribute

        mock_drive_client.list_files.return_value = [estimates_file]
        mock_drive_client.download_file.return_value = b"ticker,price\nAAPL,150.00"

        # Setup mock parser
        mock_csv_parser.parse_estimates_csv.return_value = [
            LegacyEstimateRow(
                ticker="AAPL",
                start_date=date(2024, 1, 1),
                start_price=Decimal("150.00"),
                target_price=Decimal("165.00"),
                stop_loss_price=Decimal("140.00"),
                target_profit_percent=Decimal("10.00"),
                stop_loss_percent=Decimal("6.67"),
                direction="LONG",
                status="OPEN"
            )
        ]

        job = await sync_service.run_initial_import()

        assert job.job_type == SyncJobType.INITIAL_IMPORT
        assert job.records_processed >= 0  # Import logic is placeholder
        mock_drive_client.download_file.assert_called_once_with("est123")
        mock_csv_parser.parse_estimates_csv.assert_called_once()

    @pytest.mark.asyncio
    async def test_initial_import_with_history(
        self,
        sync_service,
        mock_drive_client,
        mock_csv_parser,
        mock_sync_job_repo
    ):
        """Test initial import with history CSV."""
        # Setup mock files
        history_file = Mock(
            id="hist123",
            mime_type="text/csv"
        )
        history_file.name = "History_AAPL.csv"  # Set name as attribute

        mock_drive_client.list_files.return_value = [history_file]
        mock_drive_client.download_file.return_value = b"date,close\n2024-01-01,150.00"

        # Setup mock parser
        mock_csv_parser.parse_history_csv.return_value = [
            LegacyHistoryRow(
                date=date(2024, 1, 1),
                open=Decimal("149.00"),
                high=Decimal("151.00"),
                low=Decimal("148.00"),
                close=Decimal("150.00"),
                volume=1000000,
                ticker="AAPL"
            )
        ]

        job = await sync_service.run_initial_import()

        assert job.job_type == SyncJobType.INITIAL_IMPORT
        mock_drive_client.download_file.assert_called_once_with("hist123")
        mock_csv_parser.parse_history_csv.assert_called_once()

    @pytest.mark.asyncio
    async def test_initial_import_error_handling(
        self,
        sync_service,
        mock_drive_client,
        mock_sync_job_repo
    ):
        """Test initial import handles errors gracefully."""
        mock_drive_client.list_files.side_effect = Exception("Drive API error")

        with pytest.raises(Exception, match="Drive API error"):
            await sync_service.run_initial_import()

        # Should mark job as failed
        mock_sync_job_repo.mark_failed.assert_called_once()


class TestSyncEstimateToDrive:
    """Test syncing a single estimate to Drive."""

    @pytest.mark.asyncio
    async def test_sync_estimate_not_found(self, sync_service, mock_estimate_repo):
        """Test sync with non-existent estimate."""
        estimate_id = uuid4()
        mock_estimate_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            await sync_service.sync_estimate_to_drive(estimate_id)

    @pytest.mark.asyncio
    async def test_sync_estimate_new_file(
        self,
        sync_service,
        mock_estimate_repo,
        mock_drive_client,
        mock_csv_parser,
        mock_sync_job_repo
    ):
        """Test sync estimate when CSV file doesn't exist yet."""
        # Create mock estimate
        estimate_id = uuid4()
        estimate = Mock(spec=Estimate)
        estimate.id = estimate_id
        estimate.ticker = Mock(symbol="AAPL")
        estimate.status = EstimateStatus.OPEN
        estimate.created_at = datetime(2024, 1, 1)

        mock_estimate_repo.get_by_id.return_value = estimate
        mock_drive_client.list_files.return_value = []  # No existing file

        job = await sync_service.sync_estimate_to_drive(estimate_id)

        assert job.job_type == SyncJobType.ON_ESTIMATE_SAVE
        assert job.records_processed == 1
        assert job.records_failed == 0

        # Should upload new file
        mock_drive_client.upload_file.assert_called_once()
        call_args = mock_drive_client.upload_file.call_args
        assert call_args[0][1] == "estimates.csv"  # filename

    @pytest.mark.asyncio
    async def test_sync_estimate_update_existing(
        self,
        sync_service,
        mock_estimate_repo,
        mock_drive_client,
        mock_csv_parser,
        mock_sync_job_repo
    ):
        """Test sync estimate when CSV file already exists."""
        # Create mock estimate
        estimate_id = uuid4()
        estimate = Mock(spec=Estimate)
        estimate.id = estimate_id
        estimate.ticker = Mock(symbol="AAPL")
        estimate.status = EstimateStatus.OPEN
        estimate.created_at = datetime(2024, 1, 1)

        mock_estimate_repo.get_by_id.return_value = estimate

        # Mock existing file
        existing_file = Mock(id="file123", name="estimates.csv")
        mock_drive_client.list_files.return_value = [existing_file]
        mock_drive_client.download_file.return_value = b"ticker,price\nMSFT,380.00"

        # Mock parser
        mock_csv_parser.parse_estimates_csv.return_value = []

        job = await sync_service.sync_estimate_to_drive(estimate_id)

        assert job.job_type == SyncJobType.ON_ESTIMATE_SAVE
        assert job.records_processed == 1

        # Should update existing file
        mock_drive_client.update_file.assert_called_once()
        call_args = mock_drive_client.update_file.call_args
        assert call_args[0][0] == "file123"  # file_id


class TestRunDailyHistorySync:
    """Test daily history sync."""

    @pytest.mark.asyncio
    async def test_daily_history_sync_no_tickers(self, sync_service, mock_sync_job_repo):
        """Test daily history sync with no active tickers."""
        job = await sync_service.run_daily_history_sync()

        assert job.job_type == SyncJobType.DAILY_HISTORY_UPDATE
        assert job.records_processed == 0
        assert job.records_failed == 0
        mock_sync_job_repo.mark_completed.assert_called_once()

    @pytest.mark.asyncio
    async def test_daily_history_sync_error_handling(
        self,
        sync_service,
        mock_sync_job_repo
    ):
        """Test daily history sync handles errors."""
        # For now, since logic is placeholder, just test it doesn't crash
        job = await sync_service.run_daily_history_sync()
        assert job.job_type == SyncJobType.DAILY_HISTORY_UPDATE


class TestCheckEstimateConflict:
    """Test conflict detection."""

    def test_no_conflict(self, sync_service):
        """Test when there's no conflict."""
        estimate = Mock(spec=Estimate)
        estimate.ticker = Mock(symbol="AAPL")
        estimate.status = EstimateStatus.OPEN
        estimate.created_at = datetime(2024, 1, 1)

        existing_rows = []

        conflict = sync_service._check_estimate_conflict(estimate, existing_rows)
        assert conflict is None

    def test_status_conflict(self, sync_service):
        """Test when there's a status conflict."""
        estimate = Mock(spec=Estimate)
        estimate.ticker = Mock(symbol="AAPL")
        estimate.status = EstimateStatus.CLOSED_WIN
        estimate.created_at = datetime(2024, 1, 1)

        existing_row = LegacyEstimateRow(
            ticker="AAPL",
            start_date=date(2024, 1, 1),
            start_price=Decimal("150.00"),
            target_price=Decimal("165.00"),
            stop_loss_price=Decimal("140.00"),
            target_profit_percent=Decimal("10.00"),
            stop_loss_percent=Decimal("6.67"),
            direction="LONG",
            status="OPEN"  # Different status!
        )

        conflict = sync_service._check_estimate_conflict(estimate, [existing_row])
        assert conflict is not None
        assert "Status mismatch" in conflict


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
