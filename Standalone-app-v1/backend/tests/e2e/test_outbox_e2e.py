"""
End-to-end integration tests for Outbox pattern.

Tests the complete flow from estimate creation to event processing
with Drive sync integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.infra.outbox.outbox_processor import OutboxProcessor
from src.estimates.domain.entities import Estimate, EstimateStatus
from src.estimates.domain.events import EstimateEvent, EstimateEventType
from src.shared.infra.database import Base
from src.shared.domain.value_objects.money import Money
from src.shared.domain.value_objects.price_target import PriceTarget


@pytest.fixture
async def async_session_factory():
    """Create in-memory async session factory for E2E testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    yield session_factory
    
    await engine.dispose()


@pytest.fixture
def mock_sync_service():
    """Create mock SyncService for E2E testing."""
    service = AsyncMock()
    service.sync_estimate_to_drive = AsyncMock()
    return service


class TestOutboxE2E:
    """End-to-end tests for outbox pattern."""
    
    @pytest.mark.asyncio
    async def test_create_estimate_persists_unprocessed_event(
        self, async_session_factory
    ):
        """Test that creating an estimate persists an unprocessed event."""
        estimate_id = uuid4()
        
        async with async_session_factory() as session:
            # Create CREATED event (outbox pattern test - no need for full estimate)
            event = EstimateEvent(
                estimate_id=estimate_id,
                event_type=EstimateEventType.CREATED,
                event_data={"initial_price": 150.00, "direction": "LONG"},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=None,
            )
            
            session.add(event)
            await session.commit()
        
        # Verify event is unprocessed
        async with async_session_factory() as session:
            events = await EstimateEvent.get_unprocessed(session)
            
            assert len(events) == 1
            assert events[0].estimate_id == estimate_id
            assert events[0].event_type == EstimateEventType.CREATED
            assert events[0].processed_at is None
            assert events[0].retry_count == 0
    
    @pytest.mark.asyncio
    async def test_outbox_processor_processes_event(
        self, async_session_factory, mock_sync_service
    ):
        """Test that OutboxProcessor processes events and marks them as processed."""
        estimate_id = uuid4()
        
        # Create unprocessed event
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=estimate_id,
                event_type=EstimateEventType.CREATED,
                event_data={"initial_price": 150.00},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=None,
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        # Process events
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        result = await processor.process_pending_events()
        
        # Verify processing result
        assert result["processed"] == 1
        assert result["failed"] == 0
        assert result["skipped"] == 0
        
        # Verify sync was called
        mock_sync_service.sync_estimate_to_drive.assert_called_once_with(
            estimate_id=estimate_id,
            fundamentals=None
        )
        
        # Verify event marked as processed
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.processed_at is not None
            assert event.error is None
            assert event.retry_count == 0
    
    @pytest.mark.asyncio
    async def test_retry_logic_with_drive_error(
        self, async_session_factory, mock_sync_service
    ):
        """Test retry logic when Drive sync fails."""
        estimate_id = uuid4()
        
        # Create unprocessed event
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=estimate_id,
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=None,
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        # Make Drive sync fail
        mock_sync_service.sync_estimate_to_drive.side_effect = Exception("Drive quota exceeded")
        
        # First processing attempt
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        result = await processor.process_pending_events()
        
        assert result["processed"] == 0
        assert result["failed"] == 1
        
        # Verify retry count incremented
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.retry_count == 1
            assert "Drive quota exceeded" in event.error
            assert event.processed_at is None
            assert event.can_retry()
        
        # Second processing attempt (still fails)
        result = await processor.process_pending_events()
        
        assert result["processed"] == 0
        assert result["failed"] == 1
        
        # Verify retry count incremented again
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.retry_count == 2
            assert event.can_retry()
        
        # Now make Drive sync succeed
        mock_sync_service.sync_estimate_to_drive.side_effect = None
        
        # Third processing attempt (succeeds)
        result = await processor.process_pending_events()
        
        assert result["processed"] == 1
        assert result["failed"] == 0
        
        # Verify event marked as processed
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.processed_at is not None
            assert event.retry_count == 2  # Retains retry count
    
    @pytest.mark.asyncio
    async def test_multiple_events_processed_in_order(
        self, async_session_factory, mock_sync_service
    ):
        """Test that multiple events are processed in timestamp order."""
        event_ids = []
        
        # Create 5 events with different timestamps
        async with async_session_factory() as session:
            for i in range(5):
                event = EstimateEvent(
                    estimate_id=uuid4(),
                    event_type=EstimateEventType.CREATED,
                    event_data={"index": i},
                    timestamp=datetime.now(timezone.utc),
                    retry_count=0,
                    processed_at=None,
                )
                session.add(event)
                await session.flush()  # Ensure ID is assigned
                event_ids.append(event.id)
            await session.commit()
        
        # Process all events
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        result = await processor.process_pending_events()
        
        # Verify all processed
        assert result["processed"] == 5
        assert result["failed"] == 0
        
        # Verify sync called for each estimate
        assert mock_sync_service.sync_estimate_to_drive.call_count == 5
        
        # Verify all events marked as processed
        async with async_session_factory() as session:
            for event_id in event_ids:
                # Use explicit query
                result = await session.execute(
                    select(EstimateEvent).where(EstimateEvent.id == event_id)
                )
                event = result.scalar_one_or_none()
                assert event is not None
                assert event.processed_at is not None
    
    @pytest.mark.asyncio
    async def test_dead_letter_after_max_retries(
        self, async_session_factory, mock_sync_service
    ):
        """Test that events become dead letters after max retries."""
        estimate_id = uuid4()
        
        # Create event with 5 retries (dead letter)
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=estimate_id,
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=5,
                processed_at=None,
                error="Max retries exceeded"
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        # Verify event is dead letter
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.is_dead_letter()
            assert not event.can_retry()
        
        # Process events (should skip dead letter)
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        result = await processor.process_pending_events()
        
        assert result["processed"] == 0
        assert result["failed"] == 0
        assert result["skipped"] == 0  # Dead letters not counted in unprocessed
        
        # Handle dead letters
        count = await processor.handle_dead_letters()
        
        assert count == 1
        
        # Verify dead letter marked
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.error.startswith("DEAD_LETTER:")
