"""
Extra schemas for async processing
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from src.estimates.schemas.responses import EstimateResponse

class TaskStatusResponse(BaseModel):
    """
    Response schema for async task status tracking.
    """
    task_id: UUID
    status: str = Field(description="Pending, Processing, Completed, or Failed")
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    estimate: EstimateResponse | None = None
