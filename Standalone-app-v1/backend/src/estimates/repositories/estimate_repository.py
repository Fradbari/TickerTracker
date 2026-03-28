"""
Estimate Repository - Data access layer for Estimate entities.

Implements:
- CRUD operations with async/await
- Cursor-based pagination
- Advanced filtering
- Soft delete functionality
- Optimized queries for active estimates
"""

import base64
import json
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.estimates.domain.entities import Estimate
from src.estimates.schemas.filters import EstimateFilters
from src.shared.schemas.pagination import PageInfo, PaginatedResult, Pagination


class EstimateRepository:
    """
    Repository for Estimate entity data access.

    Provides type-safe, async methods for:
    - Creating estimates
    - Retrieving estimates (single, filtered, paginated)
    - Updating estimates
    - Soft deleting estimates

    Uses cursor-based pagination to avoid OFFSET performance issues.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository with async session factory.

        Args:
            session_factory: AsyncSessionLocal from database module
        """
        self.session_factory = session_factory

    async def create(self, estimate: Estimate) -> Estimate:
        """
        Create a new estimate in the database.

        Args:
            estimate: Estimate entity to create

        Returns:
            Created estimate with generated ID and timestamps

        Raises:
            IntegrityError: If estimate violates database constraints
        """
        async with self.session_factory() as session:
            session.add(estimate)
            await session.commit()
            await session.refresh(estimate)
            return estimate

    async def get_by_id(self, estimate_id: UUID) -> Estimate | None:
        """
        Retrieve estimate by ID.

        Args:
            estimate_id: UUID of the estimate

        Returns:
            Estimate if found, None otherwise

        Note:
            Does not return soft-deleted estimates by default
        """
        async with self.session_factory() as session:
            query = (
                select(Estimate)
                .where(Estimate.id == estimate_id)
                .where(Estimate.is_deleted is False)
                .options(selectinload(Estimate.ticker))  # Eager load ticker
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: EstimateFilters,
        pagination: Pagination
    ) -> PaginatedResult[Estimate]:
        """
        Get paginated list of estimates with filters.

        Args:
            filters: Filter criteria for estimates
            pagination: Pagination parameters (limit, cursor)

        Returns:
            PaginatedResult with estimates and page info

        Example:
            ```python
            filters = EstimateFilters(status="OPEN", ticker_id=ticker_uuid)
            pagination = Pagination(limit=20)
            result = await repo.get_all(filters, pagination)

            print(f"Found {len(result.items)} estimates")
            if result.page_info.has_next_page:
                # Use result.page_info.next_cursor for next page
                pass
            ```
        """
        async with self.session_factory() as session:
            # Build base query
            query = select(Estimate).options(selectinload(Estimate.ticker))

            # Apply filters
            conditions = []

            # Soft delete filter
            if not filters.include_deleted:
                conditions.append(Estimate.is_deleted is False)

            if filters.ticker_id:
                conditions.append(Estimate.ticker_id == filters.ticker_id)

            if filters.user_id:
                conditions.append(Estimate.user_id == filters.user_id)

            if filters.status:
                conditions.append(Estimate.status == filters.status)

            if filters.direction:
                conditions.append(Estimate.direction == filters.direction)

            if filters.created_after:
                conditions.append(Estimate.created_at >= filters.created_after)

            if filters.created_before:
                conditions.append(Estimate.created_at <= filters.created_before)

            if filters.closed_after:
                conditions.append(Estimate.closed_at >= filters.closed_after)

            if filters.closed_before:
                conditions.append(Estimate.closed_at <= filters.closed_before)

            if filters.min_confidence is not None:
                conditions.append(Estimate.ai_confidence >= filters.min_confidence)

            if filters.max_confidence is not None:
                conditions.append(Estimate.ai_confidence <= filters.max_confidence)

            if conditions:
                query = query.where(and_(*conditions))

            # Apply cursor pagination
            if pagination.cursor:
                cursor_data = self._decode_cursor(pagination.cursor)
                cursor_id = UUID(cursor_data["id"])
                cursor_created = datetime.fromisoformat(cursor_data["created_at"])

                # Cursor pagination: WHERE (created_at, id) > (cursor_created, cursor_id)
                query = query.where(
                    or_(
                        Estimate.created_at > cursor_created,
                        and_(
                            Estimate.created_at == cursor_created,
                            Estimate.id > cursor_id
                        )
                    )
                )

            # Order by created_at DESC, id DESC for consistent pagination
            query = query.order_by(Estimate.created_at.desc(), Estimate.id.desc())

            # Fetch limit + 1 to check if there's a next page
            query = query.limit(pagination.limit + 1)

            result = await session.execute(query)
            items = list(result.scalars().all())

            # Check if there's a next page
            has_next = len(items) > pagination.limit
            if has_next:
                items = items[:pagination.limit]  # Remove extra item

            # Generate next cursor
            next_cursor = None
            if has_next and items:
                last_item = items[-1]
                next_cursor = self._encode_cursor({
                    "id": str(last_item.id),
                    "created_at": last_item.created_at.isoformat()
                })

            # Build page info
            page_info = PageInfo(
                has_next_page=has_next,
                has_previous_page=pagination.cursor is not None,
                next_cursor=next_cursor,
                previous_cursor=None,  # Previous not implemented yet
            )

            return PaginatedResult(items=items, page_info=page_info)

    async def update(self, estimate: Estimate) -> Estimate:
        """
        Update an existing estimate.

        Args:
            estimate: Estimate entity with updated values

        Returns:
            Updated estimate

        Raises:
            NoResultFound: If estimate doesn't exist
        """
        async with self.session_factory() as session:
            # Merge the detached instance
            merged = await session.merge(estimate)
            await session.commit()
            await session.refresh(merged)
            return merged

    async def soft_delete(self, estimate_id: UUID) -> bool:
        """
        Soft delete an estimate (sets is_deleted=True, deleted_at=now).

        Args:
            estimate_id: UUID of estimate to delete

        Returns:
            True if deleted, False if not found or already deleted
        """
        async with self.session_factory() as session:
            query = (
                update(Estimate)
                .where(Estimate.id == estimate_id)
                .where(Estimate.is_deleted is False)
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow()
                )
            )
            result = await session.execute(query)
            await session.commit()
            return result.rowcount > 0

    async def get_active_by_ticker(self, ticker_id: UUID) -> list[Estimate]:
        """
        Get all active (OPEN status) estimates for a ticker.

        Args:
            ticker_id: UUID of the ticker

        Returns:
            List of active estimates, ordered by creation date (newest first)

        Note:
            Only returns non-deleted estimates with status='OPEN'
        """
        async with self.session_factory() as session:
            query = (
                select(Estimate)
                .where(Estimate.ticker_id == ticker_id)
                .where(Estimate.status == "OPEN")
                .where(Estimate.is_deleted is False)
                .options(selectinload(Estimate.ticker))
                .order_by(Estimate.created_at.desc())
            )
            result = await session.execute(query)
            return list(result.scalars().all())

    async def get_statistics_by_ticker(self, ticker_id: UUID) -> dict[str, int]:
        """
        Get estimate statistics for a ticker.

        Args:
            ticker_id: UUID of the ticker

        Returns:
            Dictionary with counts: {"total": 10, "open": 3, "closed_win": 5, ...}
        """
        async with self.session_factory() as session:
            # Count by status
            query = (
                select(
                    Estimate.status,
                    func.count(Estimate.id).label("count")
                )
                .where(Estimate.ticker_id == ticker_id)
                .where(Estimate.is_deleted is False)
                .group_by(Estimate.status)
            )
            result = await session.execute(query)
            rows = result.all()

            stats = {"total": 0}
            for status, count in rows:
                stats[status.lower()] = count
                stats["total"] += count

            return stats

    # Helper methods for cursor encoding/decoding

    def _encode_cursor(self, data: dict) -> str:
        """Encode cursor data to base64 string."""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()

    def _decode_cursor(self, cursor: str) -> dict:
        """Decode base64 cursor to dictionary."""
        json_str = base64.b64decode(cursor.encode()).decode()
        return json.loads(json_str)
