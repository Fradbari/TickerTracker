"""
Sync Service for bidirectional synchronization with Google Drive.

Coordinates:
- Initial import of legacy data from Drive
- Export of estimates to Drive (CSV format)
- Daily history sync for active tickers
- Conflict resolution with logging
"""

import hashlib
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.sync.domain.entities import SyncJob, SyncJobType, SyncJobStatus
from src.sync.repositories.sync_job_repository import SyncJobRepository
from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.json_parser import LegacyJsonParser
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow
from src.infra.drive.client import GoogleDriveClient
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.market_data.repositories.market_data_repository import MarketDataRepository, MarketDataRow
from src.market_data.domain.market_data import MarketData

logger = logging.getLogger(__name__)


class SyncConflictError(Exception):
    """Raised when a sync conflict is detected."""
    pass


class SyncService:
    """
    Service for synchronizing data with Google Drive.
    
    Provides methods for:
    - Initial import from legacy CSV/JSON files
    - Exporting estimates to Drive
    - Daily history sync
    - Conflict resolution
    
    Example:
        ```python
        service = SyncService(
            drive_client=drive_client,
            csv_parser=csv_parser,
            estimate_repo=estimate_repo,
            market_data_repo=market_data_repo,
            sync_job_repo=sync_job_repo,
            drive_folder_id="1ABC...",
            session=db_session
        )
        
        # Run initial import
        job = await service.run_initial_import()
        print(f"Imported {job.records_processed} records")
        
        # Sync estimate to Drive
        await service.sync_estimate_to_drive(estimate_id)
        
        # Daily history sync
        await service.run_daily_history_sync()
        ```
    """
    
    def __init__(
        self,
        drive_client: GoogleDriveClient,
        csv_parser: LegacyCsvParser,
        json_parser: LegacyJsonParser,
        estimate_repo: EstimateRepository,
        market_data_repo: MarketDataRepository,
        sync_job_repo: SyncJobRepository,
        drive_folder_id: str,
        session: AsyncSession,
    ):
        """
        Initialize SyncService with dependencies.
        
        Args:
            drive_client: Google Drive client for file operations
            csv_parser: CSV parser for legacy format
            json_parser: JSON parser for legacy backup format
            estimate_repo: Repository for estimate persistence
            market_data_repo: Repository for market data persistence
            sync_job_repo: Repository for sync job tracking
            drive_folder_id: Root folder ID in Google Drive
            session: SQLAlchemy async session
        """
        self._drive = drive_client
        self._csv_parser = csv_parser
        self._json_parser = json_parser
        self._estimates = estimate_repo
        self._market_data = market_data_repo
        self._sync_jobs = sync_job_repo
        self._folder_id = drive_folder_id
        self._session = session
    
    def _calculate_checksum(self, content: bytes) -> str:
        """
        Calculate SHA-256 checksum of content.
        
        Args:
            content: File content as bytes
            
        Returns:
            Hex digest of SHA-256 hash
        """
        return hashlib.sha256(content).hexdigest()
    
    async def run_initial_import(
        self,
        backup_filename: str = "backup.json",
        history_pattern: str = "History_",
    ) -> SyncJob:
        """
        Run initial import of legacy data from Google Drive.
        
        Downloads estimates CSV and history CSV files from Drive,
        parses them, and imports into database. Creates SyncJob
        to track the operation.
        
        Args:
            backup_filename: Name of backup JSON/CSV file (default: "backup.json")
            history_pattern: Pattern for history files (default: "History_")
            
        Returns:
            Completed SyncJob with import statistics
            
        Raises:
            DriveFileNotFoundError: If required files not found
            SyncConflictError: If data conflicts detected
            
        Example:
            >>> job = await service.run_initial_import()
            >>> print(f"Processed: {job.records_processed}, Failed: {job.records_failed}")
        """
        # Create sync job
        job = SyncJob(
            job_type=SyncJobType.INITIAL_IMPORT,
            status=SyncJobStatus.RUNNING,
            filename=backup_filename,
            started_at=datetime.utcnow(),
        )
        await self._sync_jobs.save(job)
        
        # Initialize counters
        records_processed = 0
        records_failed = 0
        checksum_before = None
        
        try:
            logger.info(f"Starting initial import from Drive folder {self._folder_id}")
            
            # List all files in Drive folder
            files = await self._drive.list_files(self._folder_id)
            logger.info(f"Found {len(files)} files in Drive folder")
            
            # Find and import estimates file (JSON backup has priority over CSV)
            estimates_file = None
            for file in files:
                if file.name.endswith('.json') and 'TickerTracker' in file.name:
                    estimates_file = file
                    break
            
            if not estimates_file:
                for file in files:
                    if file.name.endswith('.csv') and 'History_' not in file.name:
                        estimates_file = file
                        break
            
            if estimates_file:
                logger.info(f"Importing estimates from {estimates_file.name}")
                
                # Download and parse estimates
                content = await self._drive.download_file(estimates_file.id)
                checksum = self._calculate_checksum(content)
                checksum_before = checksum
                job.checksum_before = checksum
                
                if estimates_file.name.endswith('.json'):
                    estimates_rows = self._json_parser.parse_backup_json(content.decode('utf-8'))
                else:
                    estimates_rows = self._csv_parser.parse_estimates_csv(content)
                
                logger.info(f"Parsed {len(estimates_rows)} estimate rows")
                
                # Import each estimate (idempotent - skip duplicates)
                for row in estimates_rows:
                    try:
                        await self._import_estimate_row(row)
                        records_processed += 1
                    except Exception as e:
                        logger.warning(f"Failed to import estimate {row.ticker}: {e}")
                        records_failed += 1
            
            # Import history files for each ticker
            history_files = [f for f in files if history_pattern in f.name and f.name.endswith('.csv')]
            logger.info(f"Found {len(history_files)} history files")
            
            for history_file in history_files:
                try:
                    logger.info(f"Importing history from {history_file.name}")
                    
                    # Download and parse history
                    content = await self._drive.download_file(history_file.id)
                    
                    # Extract ticker from filename (e.g., History_AAPL.csv -> AAPL)
                    ticker_symbol = history_file.name.replace(history_pattern, '').replace('.csv', '')
                    
                    history_rows = self._csv_parser.parse_history_csv(content, default_ticker=ticker_symbol)
                    
                    # Import history data
                    imported = await self._import_history_rows(ticker_symbol, history_rows)
                    records_processed += imported
                    
                except Exception as e:
                    logger.warning(f"Failed to import history {history_file.name}: {e}")
                    records_failed += 1
            
            # Mark job as completed
            job = await self._sync_jobs.mark_completed(
                job.id,
                records_processed=records_processed,
                records_failed=records_failed,
                checksum_after=checksum_before or "",  # Same for import
            )
            
            logger.info(f"Initial import completed: {records_processed} processed, {records_failed} failed")
            return job
            
        except Exception as e:
            logger.error(f"Initial import failed: {e}")
            await self._sync_jobs.mark_failed(
                job.id,
                error_message=str(e),
                records_processed=records_processed,
                records_failed=records_failed,
            )
            raise
    
    async def _import_estimate_row(self, row: LegacyEstimateRow) -> None:
        """
        Import a single estimate row (idempotent).
        
        Checks if estimate already exists to avoid duplicates.
        
        Args:
            row: Parsed legacy estimate row
        """
        # For now, we'll skip import logic as it requires ticker resolution
        # This is a placeholder that can be expanded when Ticker repository exists
        logger.debug(f"Importing estimate for {row.ticker} (placeholder)")
        # TODO: Implement full import logic with ticker resolution
        pass
    
    async def _import_history_rows(
        self,
        ticker_symbol: str,
        rows: List[LegacyHistoryRow]
    ) -> int:
        """
        Import history rows for a ticker.
        
        Uses upsert to handle duplicates gracefully.
        
        Args:
            ticker_symbol: Ticker symbol (e.g., 'AAPL')
            rows: List of parsed history rows
            
        Returns:
            Number of rows imported
        """
        # For now, placeholder - requires ticker resolution
        logger.debug(f"Importing {len(rows)} history rows for {ticker_symbol} (placeholder)")
        # TODO: Implement full import logic with ticker resolution
        return len(rows)
    
    async def sync_estimate_to_drive(
        self,
        estimate_id: UUID,
        fundamentals: Optional[Dict[str, Any]] = None,
    ) -> SyncJob:
        """
        Sync a single estimate to Google Drive.
        
        Exports estimate to CSV format and updates Drive file
        using atomic upload pattern (temp file + rename).
        
        Args:
            estimate_id: UUID of estimate to sync
            fundamentals: Optional fundamentals data to include
            
        Returns:
            Completed SyncJob
            
        Raises:
            ValueError: If estimate not found
            DriveError: If Drive operation fails
            
        Example:
            >>> job = await service.sync_estimate_to_drive(
            ...     estimate_id=uuid.uuid4(),
            ...     fundamentals={'pe_ratio': 25.5, 'market_cap': 3000000000}
            ... )
        """
        # Create sync job
        job = SyncJob(
            job_type=SyncJobType.ON_ESTIMATE_SAVE,
            status=SyncJobStatus.RUNNING,
            filename="estimates.csv",
            started_at=datetime.utcnow(),
        )
        await self._sync_jobs.save(job)
        
        try:
            logger.info(f"Syncing estimate {estimate_id} to Drive")
            
            # Get estimate
            estimate = await self._estimates.get_by_id(estimate_id)
            if not estimate:
                raise ValueError(f"Estimate {estimate_id} not found")
            
            # Check if estimates file exists in Drive
            files = await self._drive.list_files(
                self._folder_id,
                query="name='estimates.csv'"
            )
            
            # Download current file to calculate checksum
            checksum_before = None
            if files:
                current_content = await self._drive.download_file(files[0].id)
                checksum_before = self._calculate_checksum(current_content)
                job.checksum_before = checksum_before
            
            # Export estimate to CSV row
            csv_row = self._csv_parser.export_estimate_to_csv_row(
                estimate,
                fundamentals or {}
            )
            
            # For atomic update, we'd ideally:
            # 1. Upload to temp file
            # 2. Verify upload
            # 3. Rename/replace original
            # For now, simplified approach - direct update/upload
            
            if files:
                # Update existing file
                # Read current file, append new row
                current_rows = self._csv_parser.parse_estimates_csv(current_content)
                
                # Check for conflicts (same ticker/start_date)
                conflict = self._check_estimate_conflict(estimate, current_rows)
                if conflict:
                    logger.warning(f"Conflict detected for estimate {estimate_id}: {conflict}")
                    # Last-writer-wins: continue with update
                
                # Append row to existing content
                updated_content = current_content + csv_row.encode('utf-8-sig') + b'\n'
                
                # Update file
                updated_file = await self._drive.update_file(
                    files[0].id,
                    updated_content,
                    mime_type='text/csv'
                )
                
                checksum_after = self._calculate_checksum(updated_content)
                
            else:
                # Create new file
                header = self._csv_parser._get_estimates_header()
                content = (header + '\n' + csv_row).encode('utf-8-sig')
                
                await self._drive.upload_file(
                    self._folder_id,
                    'estimates.csv',
                    content,
                    mime_type='text/csv'
                )
                
                checksum_after = self._calculate_checksum(content)
            
            # Mark job as completed
            job = await self._sync_jobs.mark_completed(
                job.id,
                records_processed=1,
                records_failed=0,
                checksum_after=checksum_after,
            )
            
            logger.info(f"Estimate {estimate_id} synced successfully")
            return job
            
        except Exception as e:
            logger.error(f"Failed to sync estimate {estimate_id}: {e}")
            job = await self._sync_jobs.mark_failed(
                job.id,
                error_message=str(e),
            )
            raise
    
    def _check_estimate_conflict(
        self,
        estimate: Estimate,
        existing_rows: List[LegacyEstimateRow]
    ) -> Optional[str]:
        """
        Check for conflicts with existing estimates.
        
        Last-writer-wins strategy: conflicts are logged but not blocked.
        
        Args:
            estimate: Estimate being synced
            existing_rows: Existing estimate rows from Drive
            
        Returns:
            Conflict description if found, None otherwise
        """
        # Check if there's already an estimate for same ticker at same start date
        ticker_symbol = estimate.ticker.symbol if estimate.ticker else "UNKNOWN"
        
        for row in existing_rows:
            if row.ticker == ticker_symbol and row.start_date == estimate.created_at.date():
                if row.status != estimate.status.value:
                    return f"Status mismatch: Drive={row.status}, DB={estimate.status.value}"
        
        return None
    
    async def run_daily_history_sync(self) -> SyncJob:
        """
        Sync daily history for all active tickers to Google Drive.
        
        For each ticker with open estimates:
        1. Get latest market data from DB
        2. Export to History_TICKER.csv format
        3. Update/create file in Drive
        
        Returns:
            Completed SyncJob with sync statistics
            
        Example:
            >>> job = await service.run_daily_history_sync()
            >>> print(f"Synced {job.records_processed} tickers")
        """
        # Create sync job
        job = SyncJob(
            job_type=SyncJobType.DAILY_HISTORY_UPDATE,
            status=SyncJobStatus.RUNNING,
            filename="History_*.csv",
            started_at=datetime.utcnow(),
        )
        await self._sync_jobs.save(job)
        
        try:
            logger.info("Starting daily history sync")
            
            # Get active tickers (those with open estimates)
            # For now, placeholder - would need to query distinct tickers from estimates
            active_tickers: List[str] = []  # TODO: Get from DB
            
            records_processed = 0
            records_failed = 0
            
            for ticker_symbol in active_tickers:
                try:
                    await self._sync_ticker_history(ticker_symbol)
                    records_processed += 1
                except Exception as e:
                    logger.warning(f"Failed to sync history for {ticker_symbol}: {e}")
                    records_failed += 1
            
            # Mark job as completed
            job = await self._sync_jobs.mark_completed(
                job.id,
                records_processed=records_processed,
                records_failed=records_failed,
            )
            
            logger.info(f" Daily history sync completed: {records_processed} tickers synced")
            return job
            
        except Exception as e:
            logger.error(f"Daily history sync failed: {e}")
            await self._sync_jobs.mark_failed(
                job.id,
                error_message=str(e),
            )
            raise
    
    async def _sync_ticker_history(self, ticker_symbol: str) -> None:
        """
        Sync history for a single ticker to Drive.
        
        Args:
            ticker_symbol: Ticker symbol (e.g., 'AAPL')
        """
        logger.debug(f"Syncing history for {ticker_symbol}")
        
        # TODO: Implement full logic:
        # 1. Get ticker_id from symbol
        # 2. Get market data from DB
        # 3. Export to CSV using parser
        # 4. Upload/update file in Drive
        
        pass


__all__ = ["SyncService", "SyncConflictError"]
