"""
SyncJob domain model for tracking synchronization jobs with Google Drive.

Defines:
- SyncJobType enum
- SyncJobStatus enum
- SyncJob model
"""

from __future__ import annotations

from enum import Enum as PyEnum
from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Enum as SAEnum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from src.shared.infra.database import Base


class SyncJobType(PyEnum):
    INITIAL_IMPORT = "initial_import"
    DAILY_HISTORY_UPDATE = "daily_history_update"
    ON_ESTIMATE_SAVE = "on_estimate_save"
    MANUAL_SYNC = "manual_sync"


class SyncJobStatus(PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class SyncJob(Base):
    """SyncJob model for tracking synchronization jobs with Google Drive."""

    __tablename__ = "sync_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    job_type = Column(SAEnum(SyncJobType, name="sync_job_type"), nullable=False)
    status = Column(SAEnum(SyncJobStatus, name="sync_job_status"), nullable=False, default=SyncJobStatus.PENDING)
    started_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    filename = Column(String(255), nullable=False)
    checksum_before = Column(String(64), nullable=True)
    checksum_after = Column(String(64), nullable=True)
    records_processed = Column(Integer, nullable=False, default=0)
    records_failed = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("ix_sync_jobs_started_at", "started_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<SyncJob(id={self.id}, job_type={self.job_type}, status={self.status}, "
            f"filename={self.filename}, records_processed={self.records_processed}, "
            f"records_failed={self.records_failed})>"
        )