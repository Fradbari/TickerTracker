"""
EstimateHistoryService - Service for estimate state reconstruction and audit trail.

Implements Event Sourcing patterns:
- State reconstruction at any point in time
- Complete audit trail with human-readable descriptions
- Change detection between timestamps
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.estimates.domain.events import EstimateEvent, EstimateEventType
from src.estimates.repositories.estimate_event_repository import EstimateEventRepository
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.estimates.schemas.history import (
    AuditEntry,
    Change,
    EstimateHistorySummary,
    EstimateSnapshot,
)


class EstimateHistoryService:
    """
    Service for reconstructing estimate history through event sourcing.

    This service analyzes EstimateEvent records to:
    - Rebuild estimate state at any historical point
    - Generate human-readable audit trails
    - Track field-level changes over time
    - Provide history summaries and statistics

    Performance Considerations:
    - Events are cached during reconstruction to avoid repeated queries
    - For estimates with many events (>100), consider pagination
    - Timestamps use database timezone (UTC) for consistency
    """

    def __init__(
        self,
        event_repository: EstimateEventRepository,
        estimate_repository: EstimateRepository,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """
        Initialize history service with dependencies.

        Args:
            event_repository: Repository for EstimateEvent access
            estimate_repository: Repository for current Estimate state
            session_factory: Database session factory
        """
        self.event_repo = event_repository
        self.estimate_repo = estimate_repository
        self.session_factory = session_factory

    async def get_state_at(
        self,
        estimate_id: UUID,
        at_time: datetime,
    ) -> EstimateSnapshot | None:
        """
        Reconstruct estimate state at a specific point in time.

        This method replays all events up to `at_time` to rebuild
        what the estimate looked like at that moment.

        Args:
            estimate_id: UUID of the estimate
            at_time: Point in time to reconstruct state

        Returns:
            EstimateSnapshot if events exist, None if estimate didn't exist yet

        Raises:
            ValueError: If at_time is in the future

        Example:
            ```python
            # What did this estimate look like yesterday?
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            snapshot = await service.get_state_at(uuid, yesterday)

            print(f"Status was: {snapshot.status}")
            print(f"Target was: ${snapshot.target_price}")
            ```
        """
        if at_time > datetime.now(UTC):
            raise ValueError("Cannot reconstruct state in the future")

        # Get all events up to the specified time
        events = await self.event_repo.get_events_until(estimate_id, at_time)

        if not events:
            return None  # Estimate didn't exist at this time

        # Reconstruct state by replaying events
        state = self._replay_events(events)

        # Build snapshot
        snapshot = EstimateSnapshot(
            estimate_id=estimate_id,
            at_timestamp=at_time,
            ticker_id=state["ticker_id"],
            user_id=state.get("user_id"),
            status=state["status"],
            start_price=Decimal(str(state["start_price"])),
            target_price=Decimal(str(state["target_price"])),
            stop_loss_price=Decimal(str(state["stop_loss_price"])),
            target_profit_percent=Decimal(str(state["target_profit_percent"])),
            stop_loss_percent=Decimal(str(state["stop_loss_percent"])),
            exit_price=Decimal(str(state["exit_price"])) if state.get("exit_price") else None,
            realized_pnl=Decimal(str(state["realized_pnl"])) if state.get("realized_pnl") else None,
            ai_model=state.get("ai_model"),
            ai_confidence=Decimal(str(state["ai_confidence"])) if state.get("ai_confidence") else None,
            ai_reasoning=state.get("ai_reasoning"),
            created_at=state["created_at"],
            closed_at=state.get("closed_at"),
            event_count=len(events),
        )

        return snapshot

    async def get_audit_trail(
        self,
        estimate_id: UUID,
    ) -> list[AuditEntry]:
        """
        Get complete audit trail for an estimate.

        Returns a chronologically ordered list of human-readable
        audit entries describing all events that occurred.

        Args:
            estimate_id: UUID of the estimate

        Returns:
            List of AuditEntry objects (newest first)

        Example:
            ```python
            trail = await service.get_audit_trail(uuid)

            for entry in trail:
                print(f"[{entry.timestamp}] {entry.description}")
                if entry.changed_fields:
                    print(f"  Changed: {', '.join(entry.changed_fields)}")
            ```
        """
        # Get all events (newest first for audit display)
        events = await self.event_repo.get_by_estimate_id(
            estimate_id,
            order_by_asc=False
        )

        # Convert events to human-readable audit entries
        audit_entries = []
        for event in events:
            entry = self._event_to_audit_entry(event)
            audit_entries.append(entry)

        return audit_entries

    async def get_changes_between(
        self,
        estimate_id: UUID,
        start: datetime,
        end: datetime,
    ) -> list[Change]:
        """
        Get all changes that occurred between two timestamps.

        Returns a list of field-level changes, useful for analyzing
        what was modified during a specific period.

        Args:
            estimate_id: UUID of the estimate
            start: Start timestamp (inclusive)
            end: End timestamp (inclusive)

        Returns:
            List of Change objects, chronologically ordered

        Raises:
            ValueError: If start > end

        Example:
            ```python
            # What changed this week?
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            changes = await service.get_changes_between(
                uuid,
                week_ago,
                datetime.now(timezone.utc)
            )

            for change in changes:
                print(f"{change.field_name}: {change.old_value} -> {change.new_value}")
            ```
        """
        if start > end:
            raise ValueError("Start time must be before end time")

        # Get events in the time range
        events = await self.event_repo.get_events_between(estimate_id, start, end)

        # Extract changes from events
        changes = []
        for event in events:
            event_changes = self._extract_changes_from_event(event)
            changes.extend(event_changes)

        return changes

    async def get_history_summary(
        self,
        estimate_id: UUID,
    ) -> EstimateHistorySummary | None:
        """
        Get summary statistics about an estimate's history.

        Args:
            estimate_id: UUID of the estimate

        Returns:
            EstimateHistorySummary with statistics, None if no events exist
        """
        events = await self.event_repo.get_by_estimate_id(estimate_id)

        if not events:
            return None

        # Count events by type
        event_type_counts: dict[str, int] = {}
        for event in events:
            type_str = event.event_type.value
            event_type_counts[type_str] = event_type_counts.get(type_str, 0) + 1

        # Count total changes
        total_changes = 0
        for event in events:
            changes = self._extract_changes_from_event(event)
            total_changes += len(changes)

        # Get current state
        estimate = await self.estimate_repo.get_by_id(estimate_id)
        is_closed = estimate.status in ["CLOSED_WIN", "CLOSED_LOSS", "CLOSED_MANUAL", "EXPIRED"] if estimate else False

        return EstimateHistorySummary(
            estimate_id=estimate_id,
            total_events=len(events),
            first_event_at=events[0].timestamp,
            last_event_at=events[-1].timestamp,
            event_type_counts=event_type_counts,
            total_changes=total_changes,
            is_closed=is_closed,
        )

    # Private helper methods

    def _replay_events(self, events: list[EstimateEvent]) -> dict[str, Any]:
        """
        Replay events to reconstruct state.

        Args:
            events: List of events in chronological order

        Returns:
            Dictionary representing the state after all events
        """
        state: dict[str, Any] = {}

        for event in events:
            if event.event_type == EstimateEventType.CREATED:
                # Initialize state from CREATED event
                data = event.event_data
                state["ticker_id"] = UUID(data["ticker_id"])
                state["start_price"] = data["start_price"]
                state["target_price"] = data["target_price"]
                state["stop_loss_price"] = data["stop_loss_price"]
                state["target_profit_percent"] = data["target_profit_percent"]
                state["stop_loss_percent"] = data["stop_loss_percent"]
                state["status"] = "OPEN"
                state["created_at"] = event.timestamp
                state["user_id"] = event.user_id

            elif event.event_type in [EstimateEventType.UPDATED, EstimateEventType.PRICE_UPDATED]:
                # Apply updates from UPDATED/PRICE_UPDATED events
                changes = event.event_data.get("changes", {})
                for field, value in changes.items():
                    state[field] = value

            elif event.event_type in [EstimateEventType.TARGET_HIT, EstimateEventType.STOP_HIT, EstimateEventType.CLOSED]:
                # Handle close events
                data = event.event_data
                state["exit_price"] = data.get("exit_price")
                state["realized_pnl"] = (
                    data.get("realized_pnl")
                    or data.get("pnl")
                    or data.get("profit")
                    or data.get("loss")
                )
                state["closed_at"] = event.timestamp

                # Set status based on event type
                if event.event_type == EstimateEventType.TARGET_HIT:
                    state["status"] = "CLOSED_WIN"
                elif event.event_type == EstimateEventType.STOP_HIT:
                    state["status"] = "CLOSED_LOSS"
                else:
                    # For CLOSED event, check event data for status
                    if "final_status" in data:
                        state["status"] = data["final_status"]
                    elif "status" in data:
                        state["status"] = data["status"]
                    else:
                        # Infer from PnL
                        pnl = state.get("realized_pnl")
                        if pnl is None:
                            state["status"] = "CLOSED_MANUAL"
                        else:
                            state["status"] = "CLOSED_WIN" if pnl > 0 else "CLOSED_LOSS" if pnl < 0 else "CLOSED_MANUAL"

            elif event.event_type == EstimateEventType.REOPENED:
                # Handle reopen
                state["status"] = "OPEN"
                state["exit_price"] = None
                state["realized_pnl"] = None
                state["closed_at"] = None

        return state

    def _event_to_audit_entry(self, event: EstimateEvent) -> AuditEntry:
        """
        Convert an event to a human-readable audit entry.

        Args:
            event: EstimateEvent to convert

        Returns:
            AuditEntry with human-readable description
        """
        description = ""
        changed_fields = None
        old_values = None
        new_values = None
        is_system = event.user_id is None

        if event.event_type == EstimateEventType.CREATED:
            data = event.event_data
            description = (
                f"Estimate created at ${data['start_price']:.2f}, "
                f"target ${data['target_price']:.2f} (+{data['target_profit_percent']}%), "
                f"stop ${data['stop_loss_price']:.2f} (-{data['stop_loss_percent']}%)"
            )

        elif event.event_type == EstimateEventType.PRICE_UPDATED:
            changes = event.event_data.get("changes", {})
            old = event.event_data.get("old_values", {})
            changed_fields = list(changes.keys())
            old_values = old
            new_values = changes

            # Build description of price changes
            price_changes = []
            for field in ["target_price", "stop_loss_price", "start_price"]:
                if field in changes:
                    old_val = old.get(field, 0)
                    new_val = changes[field]
                    price_changes.append(f"{field.replace('_', ' ')}: ${old_val:.2f} -> ${new_val:.2f}")

            description = "Prices updated: " + ", ".join(price_changes)

        elif event.event_type == EstimateEventType.UPDATED:
            changes = event.event_data.get("changes", {})
            old = event.event_data.get("old_values", {})
            changed_fields = list(changes.keys())
            old_values = old
            new_values = changes

            description = f"Updated fields: {', '.join(changed_fields)}"

        elif event.event_type == EstimateEventType.TARGET_HIT:
            data = event.event_data
            exit_price = data.get("exit_price", 0)
            profit = data.get("profit", data.get("pnl", 0))
            description = f"Target hit! Closed at ${exit_price:.2f} with profit of ${profit:.2f}"

        elif event.event_type == EstimateEventType.STOP_HIT:
            data = event.event_data
            exit_price = data.get("exit_price", 0)
            loss = data.get("loss", data.get("pnl", 0))
            description = f"Stop loss hit. Closed at ${exit_price:.2f} with loss of ${loss:.2f}"

        elif event.event_type == EstimateEventType.CLOSED:
            data = event.event_data
            exit_price = data.get("exit_price", 0)
            pnl = data.get("pnl", 0)
            reason = data.get("reason", "manual")
            pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"
            description = f"Closed manually ({reason}) at ${exit_price:.2f}, PnL: {pnl_str}"

        elif event.event_type == EstimateEventType.REOPENED:
            reason = event.event_data.get("reason", "unknown")
            description = f"Estimate reopened (reason: {reason})"

        return AuditEntry(
            event_id=event.id,
            estimate_id=event.estimate_id,
            event_type=event.event_type,
            timestamp=event.timestamp,
            description=description,
            changed_fields=changed_fields,
            old_values=old_values,
            new_values=new_values,
            user_id=event.user_id,
            is_system_event=is_system,
        )

    def _extract_changes_from_event(self, event: EstimateEvent) -> list[Change]:
        """
        Extract field-level changes from an event.

        Args:
            event: EstimateEvent to analyze

        Returns:
            List of Change objects
        """
        changes = []

        if event.event_type == EstimateEventType.CREATED:
            # For CREATED, create changes for all initial fields
            data = event.event_data
            for field, value in data.items():
                changes.append(Change(
                    field_name=field,
                    old_value=None,
                    new_value=value,
                    changed_at=event.timestamp,
                    event_id=event.id,
                    event_type=event.event_type,
                ))

        elif event.event_type in [EstimateEventType.UPDATED, EstimateEventType.PRICE_UPDATED]:
            # Extract from changes dict
            event_changes = event.event_data.get("changes", {})
            old_values = event.event_data.get("old_values", {})

            for field, new_value in event_changes.items():
                changes.append(Change(
                    field_name=field,
                    old_value=old_values.get(field),
                    new_value=new_value,
                    changed_at=event.timestamp,
                    event_id=event.id,
                    event_type=event.event_type,
                ))

        elif event.event_type in [EstimateEventType.TARGET_HIT, EstimateEventType.STOP_HIT, EstimateEventType.CLOSED]:
            # Status change
            data = event.event_data
            status_map = {
                EstimateEventType.TARGET_HIT: "CLOSED_WIN",
                EstimateEventType.STOP_HIT: "CLOSED_LOSS",
                EstimateEventType.CLOSED: data.get("final_status") or data.get("status", "CLOSED_MANUAL"),
            }

            changes.append(Change(
                field_name="status",
                old_value="OPEN",
                new_value=status_map[event.event_type],
                changed_at=event.timestamp,
                event_id=event.id,
                event_type=event.event_type,
            ))

            # Exit price and PnL changes
            if "exit_price" in data:
                changes.append(Change(
                    field_name="exit_price",
                    old_value=None,
                    new_value=data["exit_price"],
                    changed_at=event.timestamp,
                    event_id=event.id,
                    event_type=event.event_type,
                ))

            pnl_key = None
            for key in ["realized_pnl", "pnl", "profit", "loss"]:
                if key in data:
                    pnl_key = key
                    break
            if pnl_key:
                changes.append(Change(
                    field_name="realized_pnl",
                    old_value=None,
                    new_value=data[pnl_key],
                    changed_at=event.timestamp,
                    event_id=event.id,
                    event_type=event.event_type,
                ))

        elif event.event_type == EstimateEventType.REOPENED:
            changes.append(Change(
                field_name="status",
                old_value="CLOSED",
                new_value="OPEN",
                changed_at=event.timestamp,
                event_id=event.id,
                event_type=event.event_type,
            ))

        return changes
