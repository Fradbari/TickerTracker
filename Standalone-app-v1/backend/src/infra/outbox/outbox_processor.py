"""
Outbox Processor for reliable event processing with Drive sync.

Implements the Outbox pattern for processing EstimateEvents:
- Polls unprocessed events from database
- Processes each event in isolated transaction
- Retries failed events with exponential backoff
- Handles dead letters after max retries
"""

import logging
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.estimates.domain.events import EstimateEvent, EstimateEventType

logger = logging.getLogger(__name__)


class OutboxProcessor:
    """
    Process unprocessed EstimateEvents with Drive sync integration.
    
    This processor ensures reliable event delivery using the Outbox pattern:
    1. Events are saved atomically with estimates in same transaction
    2. Background processor polls unprocessed events
    3. Each event processed in separate transaction for isolation
    4. Failed events are retried up to 5 times
    5. Dead letters are logged for manual intervention
    
    Example:
        ```python
        processor = OutboxProcessor(session_factory, sync_service)
        
        # Process pending events
        result = await processor.process_pending_events()
        print(f"Processed: {result['processed']}, Failed: {result['failed']}")
        
        # Handle dead letters
        dead_count = await processor.handle_dead_letters()
        print(f"Dead letters found: {dead_count}")
        ```
    """
    
    # Event types that trigger Drive sync
    SYNCABLE_EVENT_TYPES = {
        EstimateEventType.CREATED,
        EstimateEventType.UPDATED,
        EstimateEventType.CLOSED,
    }
    
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        sync_service: Optional[object] = None,
    ):
        """
        Initialize OutboxProcessor.
        
        Args:
            session_factory: SQLAlchemy async session factory
            sync_service: SyncService instance (optional for graceful degradation)
        """
        self._session_factory = session_factory
        self._sync_service = sync_service
        
        if sync_service is None:
            logger.warning(
                "OutboxProcessor initialized without SyncService - "
                "Drive sync will be skipped (graceful degradation mode)"
            )
    
    async def process_pending_events(self) -> Dict[str, int]:
        """
        Process unprocessed events with Drive sync.
        
        Returns:
            Dictionary with counts: {"processed": int, "failed": int, "skipped": int}
        """
        processed = 0
        failed = 0
        skipped = 0
        
        # Get unprocessed events in separate session (read-only)
        async with self._session_factory() as session:
            events = await EstimateEvent.get_unprocessed(session, limit=100)
        
        if not events:
            logger.debug("No unprocessed events found")
            return {"processed": 0, "failed": 0, "skipped": 0}
        
        logger.info(f"Processing {len(events)} unprocessed events")
        
        # Process each event in isolated transaction
        for event in events:
            result = await self._process_single_event(event.id)
            
            if result == "processed":
                processed += 1
            elif result == "failed":
                failed += 1
            elif result == "skipped":
                skipped += 1
        
        logger.info(
            f"Outbox processing completed: "
            f"processed={processed}, failed={failed}, skipped={skipped}"
        )
        
        return {
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
        }
    
    async def _process_single_event(self, event_id: UUID) -> str:
        """
        Process single event in isolated transaction.
        
        Args:
            event_id: UUID of event to process
            
        Returns:
            Status: "processed", "failed", or "skipped"
        """
        async with self._session_factory() as session:
            try:
                # Load event
                event = await session.get(EstimateEvent, event_id)
                if not event:
                    logger.warning(f"Event {event_id} not found, skipping")
                    return "skipped"
                
                # Check if already processed (race condition)
                if event.processed_at is not None:
                    logger.debug(f"Event {event_id} already processed, skipping")
                    return "skipped"
                
                # Check if event can be retried
                if not event.can_retry():
                    logger.warning(
                        f"Event {event_id} cannot be retried "
                        f"(retry_count={event.retry_count})"
                    )
                    return "skipped"
                
                # Check if event type is syncable
                if event.event_type not in self.SYNCABLE_EVENT_TYPES:
                    logger.debug(
                        f"Event {event_id} type {event.event_type.value} "
                        f"not syncable, marking as processed"
                    )
                    event.mark_processed()
                    await session.commit()
                    return "processed"
                
                # Process event with Drive sync
                await self._sync_to_drive(event)
                
                # Mark as processed
                event.mark_processed()
                await session.commit()
                
                logger.info(
                    f"Event processed successfully",
                    extra={
                        "event_id": str(event.id),
                        "estimate_id": str(event.estimate_id),
                        "event_type": event.event_type.value,
                        "retry_count": event.retry_count,
                    }
                )
                
                return "processed"
                
            except Exception as e:
                # Rollback transaction
                await session.rollback()
                
                # Load event again for update
                event = await session.get(EstimateEvent, event_id)
                if event:
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    event.mark_failed(error_msg)
                    await session.commit()
                    
                    logger.error(
                        f"Event processing failed",
                        extra={
                            "event_id": str(event.id),
                            "estimate_id": str(event.estimate_id),
                            "event_type": event.event_type.value,
                            "retry_count": event.retry_count,
                            "error": error_msg,
                        },
                        exc_info=True
                    )
                
                return "failed"
    
    async def _sync_to_drive(self, event: EstimateEvent) -> None:
        """
        Sync estimate to Drive based on event.
        
        Args:
            event: EstimateEvent to process
            
        Raises:
            Exception: If sync fails (will be caught by caller)
        """
        if self._sync_service is None:
            logger.warning(
                f"SyncService not available, skipping Drive sync for event {event.id}"
            )
            return
        
        try:
            # Import check with graceful degradation
            if not hasattr(self._sync_service, 'sync_estimate_to_drive'):
                logger.warning(
                    f"SyncService missing sync_estimate_to_drive method, "
                    f"skipping Drive sync for event {event.id}"
                )
                return
            
            # Call sync method
            await self._sync_service.sync_estimate_to_drive(
                estimate_id=event.estimate_id,
                fundamentals=None  # Could be extracted from event_data if needed
            )
            
            logger.debug(
                f"Drive sync successful for estimate {event.estimate_id}"
            )
            
        except ImportError as e:
            logger.warning(
                f"ImportError during Drive sync, graceful degradation: {e}"
            )
            # Don't raise - treat as successful processing
            
        except Exception as e:
            # Re-raise to trigger retry logic
            logger.error(
                f"Drive sync failed for estimate {event.estimate_id}: {e}"
            )
            raise
    
    async def handle_dead_letters(self) -> int:
        """
        Handle dead letter events (max retries exceeded).
        
        Logs dead letters for manual intervention and marks them
        for future alerting (Slack/Email hook placeholder).
        
        Returns:
            Count of dead letters found
        """
        async with self._session_factory() as session:
            dead_letters = await EstimateEvent.get_dead_letters(session)
            
            if not dead_letters:
                logger.debug("No dead letter events found")
                return 0
            
            logger.error(
                f"Found {len(dead_letters)} dead letter events requiring manual intervention"
            )
            
            # Process each dead letter
            for event in dead_letters:
                # Mark as dead letter
                original_error = event.error or "Unknown error"
                event.error = f"DEAD_LETTER: {original_error}"[:500]
                
                # Log detailed information for manual intervention
                logger.error(
                    f"Dead letter event details",
                    extra={
                        "event_id": str(event.id),
                        "estimate_id": str(event.estimate_id),
                        "event_type": event.event_type.value,
                        "retry_count": event.retry_count,
                        "original_error": original_error,
                        "timestamp": event.timestamp.isoformat(),
                    }
                )
                
                # TODO: Send alert (Slack/Email webhook)
                # await self._send_dead_letter_alert(event)
            
            # Commit all dead letter updates
            await session.commit()
            
            logger.warning(
                f"Processed {len(dead_letters)} dead letter events - "
                f"manual intervention required"
            )
            
            return len(dead_letters)
