"""Repository for Estimate data access."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql import func

from estimates.domain.entities import Estimate, EstimateStatus
from estimates.schemas.filters import (
    EstimateFilters,
    Pagination,
    PaginatedResult,
    decode_cursor,
    encode_cursor,
)


class EstimateRepository:
    """Repository for CRUD operations on Estimate entities."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, estimate: Estimate) -> Estimate:
        async with self._session_factory() as session:
            async with session.begin():
                session.add(estimate)
                await session.flush()
                await session.refresh(estimate)
            return estimate

    async def get_by_id(self, estimate_id: UUID) -> Optional[Estimate]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Estimate).where(
                    and_(Estimate.id == estimate_id, Estimate.is_deleted.is_(False))
                )
            )
            return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: Optional[EstimateFilters] = None,
        pagination: Optional[Pagination] = None,
    ) -> PaginatedResult[Estimate]:
        effective_pagination = pagination or Pagination()

        query = select(Estimate)
        query = self._apply_filters(query, filters)
        query = self._apply_cursor(query, effective_pagination)
        query = self._apply_ordering(query, effective_pagination)
        query = query.limit(effective_pagination.limit + 1)

        async with self._session_factory() as session:
            result = await session.execute(query)
            estimates = list(result.scalars().all())

        has_more = len(estimates) > effective_pagination.limit
        if has_more:
            estimates = estimates[: effective_pagination.limit]

        next_cursor = None
        if estimates:
            last_item = estimates[-1]
            next_cursor = encode_cursor(last_item.created_at, last_item.id)

        return PaginatedResult(
            items=estimates,
            next_cursor=next_cursor,
            has_more=has_more,
            limit=effective_pagination.limit,
        )

    async def update(self, estimate: Estimate) -> Estimate:
        async with self._session_factory() as session:
            async with session.begin():
                merged = await session.merge(estimate)
                await session.flush()
                await session.refresh(merged)
            return merged

    async def soft_delete(self, estimate_id: UUID) -> bool:
        async with self._session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    update(Estimate)
                    .where(
                        and_(
                            Estimate.id == estimate_id,
                            Estimate.is_deleted.is_(False),
                        )
                    )
                    .values(
                        status=EstimateStatus.EXPIRED,
                        is_deleted=True,
                        deleted_at=func.now(),
                        updated_at=func.now(),
                        closed_at=func.now(),
                    )
                )
            return result.rowcount > 0

    async def get_active_by_ticker(self, ticker_id: UUID) -> List[Estimate]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Estimate).where(
                    and_(
                        Estimate.ticker_id == ticker_id,
                        Estimate.is_deleted.is_(False),
                        Estimate.status == EstimateStatus.OPEN,
                    )
                )
            )
            return list(result.scalars().all())

    def _apply_filters(self, query, filters: Optional[EstimateFilters]):
        if not filters:
            return query.where(Estimate.is_deleted.is_(False))

        if filters.ticker_id:
            query = query.where(Estimate.ticker_id == filters.ticker_id)
        if filters.user_id:
            query = query.where(Estimate.user_id == filters.user_id)
        if filters.status:
            query = query.where(Estimate.status == filters.status)
        if filters.direction:
            query = query.where(Estimate.direction == filters.direction)
        if filters.created_from:
            query = query.where(Estimate.created_at >= filters.created_from)
        if filters.created_to:
            query = query.where(Estimate.created_at <= filters.created_to)
        if not filters.include_deleted:
            query = query.where(Estimate.is_deleted.is_(False))

        return query

    def _apply_cursor(self, query, pagination: Pagination):
        if not pagination.cursor:
            return query

        cursor_created_at, cursor_id = decode_cursor(pagination.cursor)

        if pagination.sort_desc:
            return query.where(
                or_(
                    Estimate.created_at < cursor_created_at,
                    and_(
                        Estimate.created_at == cursor_created_at,
                        Estimate.id < cursor_id,
                    ),
                )
            )

        return query.where(
            or_(
                Estimate.created_at > cursor_created_at,
                and_(
                    Estimate.created_at == cursor_created_at,
                    Estimate.id > cursor_id,
                ),
            )
        )

    def _apply_ordering(self, query, pagination: Pagination):
        if pagination.sort_desc:
            return query.order_by(Estimate.created_at.desc(), Estimate.id.desc())
        return query.order_by(Estimate.created_at.asc(), Estimate.id.asc())
