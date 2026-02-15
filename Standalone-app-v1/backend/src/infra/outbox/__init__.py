"""
Outbox pattern implementation for reliable event processing.

This module provides the OutboxProcessor for processing EstimateEvents
with transactional guarantees and retry logic.
"""

from .outbox_processor import OutboxProcessor

__all__ = ["OutboxProcessor"]
