"""
Repository per SyncJob persistence.

Gestisce CRUD operations per SyncJob entity usando SQLAlchemy.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.sync.domain.entities import SyncJob, SyncJobStatus, SyncJobType


class SyncJobRepository:
    """
    Repository per SyncJob entity.

    Gestisce persistence di sync jobs nel database.

    Example:
        ```python
        repo = SyncJobRepository(db_session)

        # Create job
        job = SyncJob(
            job_type=SyncJobType.INITIAL_IMPORT,
            filename="backup.json",
            status=SyncJobStatus.RUNNING
        )
        await repo.save(job)

        # Get recent jobs
        jobs = await repo.get_recent_jobs(limit=10)
        ```
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, job: SyncJob) -> SyncJob:
        """
        Save (insert or update) sync job.

        Args:
            job: SyncJob to save

        Returns:
            Saved SyncJob
        """
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def get_by_id(self, job_id: UUID) -> SyncJob | None:
        """
        Get sync job by ID.

        Args:
            job_id: Job UUID

        Returns:
            SyncJob if found, None otherwise
        """
        stmt = select(SyncJob).where(SyncJob.id == job_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_jobs(
        self,
        job_type: SyncJobType | None = None,
        limit: int = 100
    ) -> list[SyncJob]:
        """
        Get recent sync jobs, optionally filtered by type.

        Args:
            job_type: Filter by job type (optional)
            limit: Max results

        Returns:
            List of SyncJob ordered by started_at DESC
        """
        stmt = select(SyncJob).order_by(desc(SyncJob.started_at)).limit(limit)

        if job_type:
            stmt = stmt.where(SyncJob.job_type == job_type)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_last_successful_job(
        self,
        job_type: SyncJobType
    ) -> SyncJob | None:
        """
        Get last successful job of given type.

        Useful per determinare ultimo sync time.

        Args:
            job_type: Job type to filter

        Returns:
            Last successful SyncJob or None
        """
        stmt = (
            select(SyncJob)
            .where(SyncJob.job_type == job_type)
            .where(SyncJob.status == SyncJobStatus.COMPLETED)
            .order_by(desc(SyncJob.finished_at))
            .limit(1)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_completed(
        self,
        job_id: UUID,
        records_processed: int,
        records_failed: int,
        checksum_after: str | None = None
    ) -> SyncJob:
        """
        Mark job as completed.

        Args:
            job_id: Job ID
            records_processed: Number of records processed
            records_failed: Number of failed records
            checksum_after: Checksum after sync

        Returns:
            Updated SyncJob
        """
        job = await self.get_by_id(job_id)
        if not job:
            raise ValueError(f"SyncJob {job_id} not found")

        job.status = SyncJobStatus.COMPLETED
        job.finished_at = datetime.utcnow()
        job.records_processed = records_processed
        job.records_failed = records_failed
        if checksum_after:
            job.checksum_after = checksum_after

        return await self.save(job)

    async def mark_failed(
        self,
        job_id: UUID,
        error_message: str,
        records_processed: int = 0,
        records_failed: int = 0
    ) -> SyncJob:
        """
        Mark job as failed.

        Args:
            job_id: Job ID
            error_message: Error description
            records_processed: Number of records processed before failure
            records_failed: Number of failed records

        Returns:
            Updated SyncJob
        """
        job = await self.get_by_id(job_id)
        if not job:
            raise ValueError(f"SyncJob {job_id} not found")

        job.status = SyncJobStatus.FAILED
        job.finished_at = datetime.utcnow()
        job.error_message = error_message
        job.records_processed = records_processed
        job.records_failed = records_failed

        return await self.save(job)


# Export
__all__ = ["SyncJobRepository"]
