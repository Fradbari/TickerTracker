"""
EstimateEvent Repository - Data access layer for EstimateEvent entities.

Implements:
- Event retrieval operations for event sourcing
- Timeline queries (events in time ranges)
- Chronologically ordered event streaming
- Read-only operations (events are append-only)
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.estimates.domain.events import EstimateEvent, EstimateEventType


class EstimateEventRepository:
    """
    Repository for EstimateEvent entity data access.
    
    Provides read-only, async methods for:
    - Retrieving events for an estimate
    - Querying events by time range
    - Getting events by type
    
    Note: This repository is read-only because events are append-only.
    New events are created through EstimateService, not directly.
    """
    
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository with async session factory.
        
        Args:
            session_factory: AsyncSessionLocal from database module
        """
        self.session_factory = session_factory
    
    async def get_by_estimate_id(
        self,
        estimate_id: UUID,
        order_by_asc: bool = True
    ) -> List[EstimateEvent]:
        """
        Get all events for an estimate, ordered chronologically.
        
        Args:
            estimate_id: UUID of the estimate
            order_by_asc: If True, oldest first (for replay). If False, newest first.
            
        Returns:
            List of events ordered by timestamp
            
        Example:
            ```python
            # Get events for replay (oldest first)
            events = await repo.get_by_estimate_id(uuid, order_by_asc=True)
            
            # Get recent activity (newest first)
            recent = await repo.get_by_estimate_id(uuid, order_by_asc=False)
            ```
        """
        async with self.session_factory() as session:
            query = (
                select(EstimateEvent)
                .where(EstimateEvent.estimate_id == estimate_id)
            )
            
            if order_by_asc:
                query = query.order_by(EstimateEvent.timestamp.asc())
            else:
                query = query.order_by(EstimateEvent.timestamp.desc())
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_events_until(
        self,
        estimate_id: UUID,
        until: datetime
    ) -> List[EstimateEvent]:
        """
        Get all events for an estimate up to a specific timestamp.
        
        Args:
            estimate_id: UUID of the estimate
            until: Retrieve events with timestamp <= this value
            
        Returns:
            List of events ordered chronologically (oldest first)
            
        Use Case:
            Reconstruct estimate state at a specific point in time
        """
        async with self.session_factory() as session:
            query = (
                select(EstimateEvent)
                .where(
                    and_(
                        EstimateEvent.estimate_id == estimate_id,
                        EstimateEvent.timestamp <= until
                    )
                )
                .order_by(EstimateEvent.timestamp.asc())
            )
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_events_between(
        self,
        estimate_id: UUID,
        start: datetime,
        end: datetime
    ) -> List[EstimateEvent]:
        """
        Get events for an estimate within a time range.
        
        Args:
            estimate_id: UUID of the estimate
            start: Start timestamp (inclusive)
            end: End timestamp (inclusive)
            
        Returns:
            List of events ordered chronologically
            
        Use Case:
            Analyze changes that occurred during a specific period
        """
        async with self.session_factory() as session:
            query = (
                select(EstimateEvent)
                .where(
                    and_(
                        EstimateEvent.estimate_id == estimate_id,
                        EstimateEvent.timestamp >= start,
                        EstimateEvent.timestamp <= end
                    )
                )
                .order_by(EstimateEvent.timestamp.asc())
            )
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_by_event_type(
        self,
        estimate_id: UUID,
        event_type: EstimateEventType
    ) -> List[EstimateEvent]:
        """
        Get all events of a specific type for an estimate.
        
        Args:
            estimate_id: UUID of the estimate
            event_type: Type of event to retrieve
            
        Returns:
            List of events of the specified type, ordered chronologically
            
        Example:
            ```python
            # Get all price updates
            price_updates = await repo.get_by_event_type(
                uuid,
                EstimateEventType.PRICE_UPDATED
            )
            ```
        """
        async with self.session_factory() as session:
            query = (
                select(EstimateEvent)
                .where(
                    and_(
                        EstimateEvent.estimate_id == estimate_id,
                        EstimateEvent.event_type == event_type
                    )
                )
                .order_by(EstimateEvent.timestamp.asc())
            )
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def get_latest_event(
        self,
        estimate_id: UUID
    ) -> Optional[EstimateEvent]:
        """
        Get the most recent event for an estimate.
        
        Args:
            estimate_id: UUID of the estimate
            
        Returns:
            Most recent event or None if no events exist
        """
        async with self.session_factory() as session:
            query = (
                select(EstimateEvent)
                .where(EstimateEvent.estimate_id == estimate_id)
                .order_by(EstimateEvent.timestamp.desc())
                .limit(1)
            )
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def count_events(
        self,
        estimate_id: UUID
    ) -> int:
        """
        Count total number of events for an estimate.
        
        Args:
            estimate_id: UUID of the estimate
            
        Returns:
            Number of events
        """
        async with self.session_factory() as session:
            from sqlalchemy import func
            
            query = (
                select(func.count(EstimateEvent.id))
                .where(EstimateEvent.estimate_id == estimate_id)
            )
            
            result = await session.execute(query)
            return result.scalar_one()
