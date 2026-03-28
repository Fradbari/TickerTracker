"""
AiModelRun domain model for tracking AI model executions.

Defines:
- AiModelRun model
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.shared.infra.database import Base


class AiModelRun(Base):
    """AiModelRun model for tracking AI model executions."""

    __tablename__ = "ai_model_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    estimate_id = Column(UUID(as_uuid=True), ForeignKey("estimates.id"), nullable=True)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50), nullable=False)
    prompt_hash = Column(String(64), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    latency_ms = Column(Integer, nullable=False, default=0)
    output_summary = Column(Text, nullable=True)
    raw_response = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ai_model_runs_model_name_created_at", "model_name", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AiModelRun(id={self.id}, model_name={self.model_name}, model_version={self.model_version}, "
            f"prompt_tokens={self.prompt_tokens}, completion_tokens={self.completion_tokens}, latency_ms={self.latency_ms})>"
        )
