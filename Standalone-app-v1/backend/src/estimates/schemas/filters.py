"""Pydantic schemas for estimate filtering and pagination."""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from estimates.domain.entities import Direction, EstimateStatus


T = TypeVar("T")


class EstimateFilters(BaseModel):
    """Filters for querying estimates."""

    ticker_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    status: Optional[EstimateStatus] = None
    direction: Optional[Direction] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    include_deleted: bool = False


class Pagination(BaseModel):
    """Cursor-based pagination parameters."""

    limit: int = Field(default=50, ge=1, le=200)
    cursor: Optional[str] = None
    sort_desc: bool = True


class PaginatedResult(GenericModel, Generic[T]):
    """Paginated results container."""

    items: List[T]
    next_cursor: Optional[str]
    has_more: bool
    limit: int


def encode_cursor(created_at: datetime, estimate_id: UUID) -> str:
    """Encode a cursor from timestamp and UUID."""

    raw = f"{created_at.isoformat()}|{estimate_id}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    """Decode a cursor into timestamp and UUID."""

    raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
    created_at_str, estimate_id_str = raw.split("|", 1)
    return datetime.fromisoformat(created_at_str), UUID(estimate_id_str)
