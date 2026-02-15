"""
Unit tests for OutboxProcessor.

Tests the outbox pattern implementation for reliable event processing
with Drive sync integration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.infra.outbox.outbox_processor import OutboxProcessor
from src.estimates.domain.events import EstimateEvent, EstimateEventType
from src.shared.infra.database import Base


@pytest.fixture
async def async_session_factory():
    """Create in-memory async session factory for testing."""
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
    """Create mock SyncService."""
    service = AsyncMock()
    service.sync_estimate_to_drive = AsyncMock()
    return service


@pytest.fixture
async def sample_event(async_session_factory):
    """Create a sample unprocessed event."""
    async with async_session_factory() as session:
        event = EstimateEvent(
            estimate_id=uuid4(),
            event_type=EstimateEventType.CREATED,
            event_data={"initial_price": 100.0},
            timestamp=datetime.now(timezone.utc),
            retry_count=0,
            processed_at=None,
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)
        return event


class TestOutboxProcessorInit:
    """Test OutboxProcessor initialization."""
    
    def test_init_with_sync_service(self, async_session_factory, mock_sync_service):
        """Test initialization with SyncService."""
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        assert processor._session_factory == async_session_factory
        assert processor._sync_service == mock_sync_service
    
    def test_init_without_sync_service(self, async_session_factory):
        """Test initialization without SyncService (graceful degradation)."""
        processor = OutboxProcessor(async_session_factory, None)
        
        assert processor._session_factory == async_session_factory
        assert processor._sync_service is None


class TestProcessSingleEvent:
    """Test single event processing."""
    
    @pytest.mark.asyncio
    async def test_process_single_event_success(
        self, async_session_factory, mock_sync_service, sample_event
    ):
        """Test successful event processing."""
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor._process_single_event(sample_event.id)
        
        assert result == "processed"
        mock_sync_service.sync_estimate_to_drive.assert_called_once_with(
            estimate_id=sample_event.estimate_id,
            fundamentals=None
        )
        
        # Verify event marked as processed
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, sample_event.id)
            assert event.processed_at is not None
            assert event.error is None
    
    @pytest.mark.asyncio
    async def test_process_event_failure_increments_retry(
        self, async_session_factory, mock_sync_service, sample_event
    ):
        """Test failed event processing increments retry count."""
        # Make sync_estimate_to_drive raise exception
        mock_sync_service.sync_estimate_to_drive.side_effect = Exception("Drive error")
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor._process_single_event(sample_event.id)
        
        assert result == "failed"
        
        # Verify retry count incremented and error recorded
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, sample_event.id)
            assert event.retry_count == 1
            assert event.error is not None
            assert "Drive error" in event.error
            assert event.processed_at is None
    
    @pytest.mark.asyncio
    async def test_process_non_syncable_event_type_skipped(
        self, async_session_factory, mock_sync_service
    ):
        """Test non-syncable event types are marked as processed without sync."""
        # Create PRICE_UPDATED event (not in SYNCABLE_EVENT_TYPES)
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.PRICE_UPDATED,
                event_data={"old_price": 100.0, "new_price": 110.0},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=None,
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor._process_single_event(event_id)
        
        assert result == "processed"
        mock_sync_service.sync_estimate_to_drive.assert_not_called()
        
        # Verify event marked as processed
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.processed_at is not None
    
    @pytest.mark.asyncio
    async def test_process_already_processed_event_skipped(
        self, async_session_factory, mock_sync_service
    ):
        """Test already processed events are skipped."""
        # Create already processed event
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=datetime.now(timezone.utc),
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor._process_single_event(event_id)
        
        assert result == "skipped"
        mock_sync_service.sync_estimate_to_drive.assert_not_called()


class TestDeadLetterHandling:
    """Test dead letter handling."""
    
    @pytest.mark.asyncio
    async def test_dead_letter_after_5_failures(
        self, async_session_factory, mock_sync_service
    ):
        """Test event becomes dead letter after 5 failed retries."""
        # Create event with 4 retries
        async with async_session_factory() as session:
            event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=4,
                processed_at=None,
                error="Previous error"
            )
            session.add(event)
            await session.commit()
            event_id = event.id
        
        # Make sync fail (5th retry)
        mock_sync_service.sync_estimate_to_drive.side_effect = Exception("Final error")
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor._process_single_event(event_id)
        
        assert result == "failed"
        
        # Verify event is now dead letter
        async with async_session_factory() as session:
            event = await session.get(EstimateEvent, event_id)
            assert event.retry_count == 5
            assert event.is_dead_letter()
            assert not event.can_retry()
    
    @pytest.mark.asyncio
    async def test_handle_dead_letters(self, async_session_factory, mock_sync_service):
        """Test handle_dead_letters marks and logs dead letters."""
        # Create multiple dead letter events
        event_ids = []
        async with async_session_factory() as session:
            for i in range(3):
                event = EstimateEvent(
                    estimate_id=uuid4(),
                    event_type=EstimateEventType.CREATED,
                    event_data={},
                    timestamp=datetime.now(timezone.utc),
                    retry_count=5,
                    processed_at=None,
                    error=f"Error {i}"
                )
                session.add(event)
                await session.flush()  # Ensure ID is assigned
                event_ids.append(event.id)
            await session.commit()
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        count = await processor.handle_dead_letters()
        
        assert count == 3
        
        # Verify all dead letters marked
        async with async_session_factory() as session:
            for event_id in event_ids:
                # Use explicit query to reload from database
                result = await session.execute(
                    select(EstimateEvent).where(EstimateEvent.id == event_id)
                )
                event = result.scalar_one_or_none()
                assert event is not None, f"Event {event_id} not found"
                assert event.error is not None, f"Event {event_id} has no error"
                assert event.error.startswith("DEAD_LETTER:"), \
                    f"Event {event_id} error is '{event.error}', expected to start with 'DEAD_LETTER:'"


class TestEventIsolation:
    """Test transaction isolation for events."""
    
    @pytest.mark.asyncio
    async def test_event_isolation_one_failure_doesnt_block_others(
        self, async_session_factory, mock_sync_service
    ):
        """Test that one failed event doesn't block processing of others."""
        # Create 10 events
        event_ids = []
        failing_estimate_id = None
        failing_event_id = None
        
        async with async_session_factory() as session:
            for i in range(10):
                estimate_id = uuid4()
                event = EstimateEvent(
                    estimate_id=estimate_id,
                    event_type=EstimateEventType.CREATED,
                    event_data={"index": i},
                    timestamp=datetime.now(timezone.utc),
                    retry_count=0,
                    processed_at=None,
                )
                session.add(event)
                await session.flush()  # Get event.id
                event_ids.append(event.id)
                if i == 5:
                    failing_estimate_id = estimate_id
                    failing_event_id = event.id
            await session.commit()
        
        # Make 6th event fail
        async def side_effect_func(estimate_id, fundamentals=None):
            if estimate_id == failing_estimate_id:
                raise Exception("Simulated error")
        
        mock_sync_service.sync_estimate_to_drive = AsyncMock(side_effect=side_effect_func)
        
        processor = OutboxProcessor(async_session_factory, mock_sync_service)
        
        result = await processor.process_pending_events()
        
        # Should process 9 successfully, 1 failed
        assert result["processed"] == 9
        assert result["failed"] == 1
        assert result["skipped"] == 0
        
        # Verify failing event marked as failed
        async with async_session_factory() as session:
            result = await session.execute(
                select(EstimateEvent).where(EstimateEvent.id == failing_event_id)
            )
            event = result.scalar_one_or_none()
            assert event is not None
            assert event.retry_count == 1
            assert event.processed_at is None
            
            # Verify others processed successfully
            for event_id in event_ids:
                if event_id != failing_event_id:
                    result = await session.execute(
                        select(EstimateEvent).where(EstimateEvent.id == event_id)
                    )
                    event = result.scalar_one_or_none()
                    assert event is not None
                    assert event.processed_at is not None
                    assert event.retry_count == 0


class TestGetUnprocessed:
    """Test get_unprocessed query logic."""
    
    @pytest.mark.asyncio
    async def test_get_unprocessed_excludes_processed(self, async_session_factory):
        """Test that get_unprocessed excludes already processed events."""
        async with async_session_factory() as session:
            # Create processed event
            processed_event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=datetime.now(timezone.utc),
            )
            
            # Create unprocessed event
            unprocessed_event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=0,
                processed_at=None,
            )
            
            session.add_all([processed_event, unprocessed_event])
            await session.commit()
            
            # Get unprocessed events
            events = await EstimateEvent.get_unprocessed(session, limit=100)
            
            assert len(events) == 1
            assert events[0].id == unprocessed_event.id
            assert events[0].processed_at is None
    
    @pytest.mark.asyncio
    async def test_get_unprocessed_excludes_dead_letters(self, async_session_factory):
        """Test that get_unprocessed excludes dead letters (retry_count >= 5)."""
        async with async_session_factory() as session:
            # Create dead letter event
            dead_letter_event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=5,
                processed_at=None,
            )
            
            # Create retryable event
            retryable_event = EstimateEvent(
                estimate_id=uuid4(),
                event_type=EstimateEventType.CREATED,
                event_data={},
                timestamp=datetime.now(timezone.utc),
                retry_count=2,
                processed_at=None,
            )
            
            session.add_all([dead_letter_event, retryable_event])
            await session.commit()
            
            # Get unprocessed events
            events = await EstimateEvent.get_unprocessed(session, limit=100)
            
            assert len(events) == 1
            assert events[0].id == retryable_event.id
            assert events[0].retry_count < 5
