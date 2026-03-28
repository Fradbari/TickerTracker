"""
Estimate Service - Business logic orchestration for estimates.

This service layer coordinates estimate operations, enforces business rules,
and publishes domain events.
"""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.estimates.domain.entities import Direction, Estimate, EstimateStatus
from src.estimates.domain.events import EstimateEvent, EstimateEventType
from src.estimates.domain.pnl import calculate_pnl
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.estimates.schemas.commands import (
    CloseEstimateCommand,
    CreateEstimateCommand,
    UpdateEstimateCommand,
)
from src.estimates.services.exceptions import (
    EstimateAlreadyClosedError,
    EstimateNotFoundError,
    InvalidPriceError,
    MarketDataNotAvailableError,
    TickerNotFoundError,
)
from src.market_data.domain.entities import Ticker
from src.market_data.repositories.market_data_repository import MarketDataRepository


class EstimateService:
    """
    Service for estimate business logic and orchestration.

    Responsibilities:
    - Validate business rules
    - Orchestrate repository operations
    - Calculate prices and PnL
    - Publish domain events (via EstimateEvent)
    - Ensure transactional consistency

    Dependencies are injected via constructor for testing and flexibility.
    """

    def __init__(
        self,
        estimate_repo: EstimateRepository,
        market_data_repo: MarketDataRepository,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        """
          Initialize service with repository dependencies.

        Args:
            estimate_repo: Repository for estimate data access
            market_data_repo: Repository for market data access
            session_factory: Async session factory for database operations
        """
        self._estimate_repo = estimate_repo
        self._market_data_repo = market_data_repo
        self._session_factory = session_factory

    async def create_estimate(
        self, command: CreateEstimateCommand
    ) -> Estimate:
        """
        Create a new estimate with calculated prices and publish CREATED event.

        Business logic:
        1. Validate ticker exists
        2. Get current market price
        3. Calculate target_price and stop_loss_price from percentages
        4. Create Estimate entity
        5. Publish ESTIMATE_CREATED event
        6. Save both estimate and event atomically

        Args:
            command: CreateEstimateCommand with ticker_id, direction, and percentages

        Returns:
            Created Estimate entity with calculated prices

        Raises:
            TickerNotFoundError: If ticker_id does not exist
            MarketDataNotAvailableError: If no market data available for ticker
            InvalidPriceError: If calculated prices are invalid
        """
        # Validate ticker exists
        ticker = await self._get_ticker(command.ticker_id)
        if not ticker:
            raise TickerNotFoundError(command.ticker_id)

        # Get current market price
        current_price = await self._get_current_price(command.ticker_id)

        # Calculate target and stop loss prices
        target_price, stop_loss_price = self._calculate_prices(
            start_price=current_price,
            direction=command.direction,
            target_percent=command.target_profit_percent,
            stop_percent=command.stop_loss_percent,
        )

        # Validate calculated prices
        self._validate_prices(
            start_price=current_price,
            target_price=target_price,
            stop_loss_price=stop_loss_price,
            direction=command.direction,
        )

        # Create estimate entity
        estimate = Estimate(
            id=uuid.uuid4(),
            ticker_id=command.ticker_id,
            user_id=command.user_id,
            start_price=current_price,
            target_price=target_price,
            stop_loss_price=stop_loss_price,
            target_profit_percent=command.target_profit_percent,
            stop_loss_percent=command.stop_loss_percent,
            status=EstimateStatus.OPEN,
            direction=Direction[command.direction],
            ai_model=command.ai_model,
            ai_confidence=command.ai_confidence,
            ai_reasoning=command.ai_reasoning,
        )

        # Create CREATED event
        event = EstimateEvent(
            id=uuid.uuid4(),
            estimate_id=estimate.id,
            event_type=EstimateEventType.CREATED,
            event_data={
                "ticker_id": str(command.ticker_id),
                "start_price": float(current_price),
                "target_price": float(target_price),
                "stop_loss_price": float(stop_loss_price),
                "direction": command.direction,
                "target_profit_percent": float(command.target_profit_percent),
                "stop_loss_percent": float(command.stop_loss_percent),
            },
            user_id=command.user_id,
            timestamp=datetime.now(UTC),
        )

        # Save estimate and event atomically
        async with self._session_factory() as session:
            async with session.begin():
                session.add(estimate)
                session.add(event)
            # Refresh outside transaction to get database-generated fields
            await session.refresh(estimate)

        return estimate

    async def update_estimate(
        self, command: UpdateEstimateCommand
    ) -> Estimate:
        """
        Update an existing estimate and publish UPDATED event.

        Business logic:
        1. Validate estimate exists and is OPEN
        2. Recalculate prices if percentages changed
        3. Update estimate fields
        4. Publish PRICE_UPDATED or UPDATED event
        5. Save changes atomically

        Args:
            command: UpdateEstimateCommand with estimate_id and fields to update

        Returns:
            Updated Estimate entity

        Raises:
            EstimateNotFoundError: If estimate does not exist
            EstimateAlreadyClosedError: If estimate is not OPEN
        """
        # Get existing estimate
        estimate = await self._estimate_repo.get_by_id(command.estimate_id)
        if not estimate:
            raise EstimateNotFoundError(command.estimate_id)

        # Validate estimate is open
        if estimate.status != EstimateStatus.OPEN:
            raise EstimateAlreadyClosedError(command.estimate_id, estimate.status.value)

        # Track changes for event
        changes = {}
        old_values = {}

        # Update percentages and recalculate prices if needed
        prices_updated = False
        if command.target_profit_percent is not None or command.stop_loss_percent is not None:
            new_target_percent = command.target_profit_percent or estimate.target_profit_percent
            new_stop_percent = command.stop_loss_percent or estimate.stop_loss_percent

            # Recalculate prices
            new_target_price, new_stop_price = self._calculate_prices(
                start_price=estimate.start_price,
                direction=estimate.direction.value,
                target_percent=new_target_percent,
                stop_percent=new_stop_percent,
            )

            # Update if changed
            if command.target_profit_percent is not None:
                old_values["target_profit_percent"] = float(estimate.target_profit_percent)
                old_values["target_price"] = float(estimate.target_price)
                estimate.target_profit_percent = command.target_profit_percent
                estimate.target_price = new_target_price
                changes["target_profit_percent"] = float(command.target_profit_percent)
                changes["target_price"] = float(new_target_price)
                prices_updated = True

            if command.stop_loss_percent is not None:
                old_values["stop_loss_percent"] = float(estimate.stop_loss_percent)
                old_values["stop_loss_price"] = float(estimate.stop_loss_price)
                estimate.stop_loss_percent = command.stop_loss_percent
                estimate.stop_loss_price = new_stop_price
                changes["stop_loss_percent"] = float(command.stop_loss_percent)
                changes["stop_loss_price"] = float(new_stop_price)
                prices_updated = True

        # Update AI fields
        if command.ai_confidence is not None:
            old_values["ai_confidence"] = float(estimate.ai_confidence) if estimate.ai_confidence else None
            estimate.ai_confidence = command.ai_confidence
            changes["ai_confidence"] = float(command.ai_confidence)

        if command.ai_reasoning is not None:
            old_values["ai_reasoning"] = estimate.ai_reasoning
            estimate.ai_reasoning = command.ai_reasoning
            changes["ai_reasoning"] = command.ai_reasoning

        # Determine event type
        event_type = EstimateEventType.PRICE_UPDATED if prices_updated else EstimateEventType.UPDATED

        # Create event
        event = EstimateEvent(
            id=uuid.uuid4(),
            estimate_id=estimate.id,
            event_type=event_type,
            event_data={
                "changes": changes,
                "old_values": old_values,
            },
            user_id=command.user_id,
            timestamp=datetime.now(UTC),
        )

        # Save atomically
        async with self._session_factory() as session:
            async with session.begin():
                estimate = await session.merge(estimate)
                session.add(event)
            # Refresh to get updated fields
            await session.refresh(estimate)

        return estimate

    async def close_estimate(
        self,
        command: CloseEstimateCommand,
    ) -> Estimate:
        """
        Manually close an estimate and calculate realized PnL.

        Business logic:
        1. Validate estimate exists and is OPEN
        2. Calculate realized PnL based on direction
        3. Determine close status (WIN/LOSS/MANUAL)
        4. Update estimate with exit data
        5. Publish CLOSED event
        6. Save changes atomically

        Args:
            command: CloseEstimateCommand with estimate_id, exit_price, and reason

        Returns:
            Closed Estimate entity with PnL calculated

        Raises:
            EstimateNotFoundError: If estimate does not exist
            EstimateAlreadyClosedError: If estimate is already closed
            InvalidPriceError: If exit_price is invalid
        """
        # Get estimate
        estimate = await self._estimate_repo.get_by_id(command.estimate_id)
        if not estimate:
            raise EstimateNotFoundError(command.estimate_id)

        # Validate is open
        if estimate.status != EstimateStatus.OPEN:
            raise EstimateAlreadyClosedError(command.estimate_id, estimate.status.value)

        # Validate exit price
        if command.exit_price <= 0:
            raise InvalidPriceError(
                "Exit price must be positive",
                {"exit_price": float(command.exit_price)}
            )

        # Calculate realized PnL
        pnl = calculate_pnl(
            start_price=estimate.start_price,
            exit_price=command.exit_price,
            direction=estimate.direction.value,
        )

        # Determine status based on PnL
        if pnl > 0:
            new_status = EstimateStatus.CLOSED_WIN
        elif pnl < 0:
            new_status = EstimateStatus.CLOSED_LOSS
        else:
            new_status = EstimateStatus.CLOSED_MANUAL

        # Update estimate
        estimate.exit_price = command.exit_price
        estimate.realized_pnl = pnl
        estimate.status = new_status
        estimate.closed_at = datetime.now(UTC)

        # Create CLOSED event
        event = EstimateEvent(
            id=uuid.uuid4(),
            estimate_id=estimate.id,
            event_type=EstimateEventType.CLOSED,
            event_data={
                "exit_price": float(command.exit_price),
                "realized_pnl": float(pnl),
                "reason": command.reason,
                "final_status": new_status.value,
            },
            user_id=command.user_id,
            timestamp=datetime.now(UTC),
        )

        # Save atomically
        async with self._session_factory() as session:
            async with session.begin():
                estimate = await session.merge(estimate)
                session.add(event)
            # Refresh to get updated fields
            await session.refresh(estimate)

        return estimate

    async def check_and_update_targets(
        self,
        estimate_id: UUID,
        current_price: Decimal | None = None,
    ) -> Estimate | None:
        """
        Check if estimate hit target or stop loss and update accordingly.

        This method is typically called by a background worker to automatically
        close estimates when market conditions trigger target or stop loss.

        Business logic:
        1. Get estimate and validate is OPEN
        2. Get current price if not provided
        3. Check if target hit or stop hit based on direction
        4. If hit, close estimate automatically with appropriate event
        5. Return closed estimate or None if no action taken

        Args:
            estimate_id: UUID of the estimate to check
            current_price: Optional current price (fetched if not provided)

        Returns:
            Updated Estimate if target/stop hit, None otherwise

        Raises:
            EstimateNotFoundError: If estimate does not exist
            MarketDataNotAvailableError: If cannot get current price
        """
        # Get estimate
        estimate = await self._estimate_repo.get_by_id(estimate_id)
        if not estimate:
            raise EstimateNotFoundError(estimate_id)

        # Skip if not OPEN
        if estimate.status != EstimateStatus.OPEN:
            return None

        # Get current price
        if current_price is None:
            current_price = await self._get_current_price(estimate.ticker_id)

        # Check target/stop based on direction
        target_hit = False
        stop_hit = False

        if estimate.direction == Direction.LONG:
            target_hit = current_price >= estimate.target_price
            stop_hit = current_price <= estimate.stop_loss_price
        else:  # SHORT
            target_hit = current_price <= estimate.target_price
            stop_hit = current_price >= estimate.stop_loss_price

        # No action if neither hit
        if not target_hit and not stop_hit:
            return None

        # Determine which was hit and close accordingly
        if target_hit:
            event_type = EstimateEventType.TARGET_HIT
            reason = "Target price reached"
            final_status = EstimateStatus.CLOSED_WIN
        else:  # stop_hit
            event_type = EstimateEventType.STOP_HIT
            reason = "Stop loss triggered"
            final_status = EstimateStatus.CLOSED_LOSS

        # Calculate PnL
        pnl = calculate_pnl(
            start_price=estimate.start_price,
            exit_price=current_price,
            direction=estimate.direction.value,
        )

        # Update estimate
        estimate.exit_price = current_price
        estimate.realized_pnl = pnl
        estimate.status = final_status
        estimate.closed_at = datetime.now(UTC)

        # Create event (TARGET_HIT or STOP_HIT, then CLOSED)
        trigger_event = EstimateEvent(
            id=uuid.uuid4(),
            estimate_id=estimate.id,
            event_type=event_type,
            event_data={
                "exit_price": float(current_price),
                "target_price": float(estimate.target_price),
                "stop_loss_price": float(estimate.stop_loss_price),
                "realized_pnl": float(pnl),
            },
            user_id=None,  # System event
            timestamp=datetime.now(UTC),
        )

        closed_event = EstimateEvent(
            id=uuid.uuid4(),
            estimate_id=estimate.id,
            event_type=EstimateEventType.CLOSED,
            event_data={
                "exit_price": float(current_price),
                "realized_pnl": float(pnl),
                "reason": reason,
                "final_status": final_status.value,
                "auto_closed": True,
            },
            user_id=None,  # System event
            timestamp=datetime.now(UTC),
        )

        # Save atomically
        async with self._session_factory() as session:
            async with session.begin():
                estimate = await session.merge(estimate)
                session.add(trigger_event)
                session.add(closed_event)
            # Refresh to get updated fields
            await session.refresh(estimate)

        return estimate

    # --- Private helper methods ---

    async def _get_ticker(self, ticker_id: UUID) -> Ticker | None:
        """Get ticker by ID."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(Ticker).where(Ticker.id == ticker_id)
            )
            return result.scalar_one_or_none()

    async def _get_current_price(self, ticker_id: UUID) -> Decimal:
        """
        Get current market price for ticker.

        Uses latest available market data from repository.

        Raises:
            MarketDataNotAvailableError: If no data available
        """
        latest_data = await self._market_data_repo.get_latest_price(ticker_id)

        if not latest_data:
            raise MarketDataNotAvailableError(
                ticker_id,
                "No market data found for this ticker"
            )

        # Use close price as current price
        return latest_data.close

    def _calculate_prices(
        self,
        start_price: Decimal,
        direction: str,
        target_percent: Decimal,
        stop_percent: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """
        Calculate target and stop loss prices from percentages.

        For LONG:
            target = start_price * (1 + target_percent / 100)
            stop = start_price * (1 - stop_percent / 100)

        For SHORT:
            target = start_price * (1 - target_percent / 100)
            stop = start_price * (1 + stop_percent / 100)

        Returns:
            Tuple of (target_price, stop_loss_price)
        """
        if direction == "LONG":
            target_price = start_price * (1 + target_percent / 100)
            stop_loss_price = start_price * (1 - stop_percent / 100)
        else:  # SHORT
            target_price = start_price * (1 - target_percent / 100)
            stop_loss_price = start_price * (1 + stop_percent / 100)

        # Round to 4 decimal places
        target_price = target_price.quantize(Decimal("0.0001"))
        stop_loss_price = stop_loss_price.quantize(Decimal("0.0001"))

        return target_price, stop_loss_price

    def _validate_prices(
        self,
        start_price: Decimal,
        target_price: Decimal,
        stop_loss_price: Decimal,
        direction: str,
    ) -> None:
        """
        Validate that calculated prices are logical.

        For LONG: stop < start < target
        For SHORT: target < start < stop

        Raises:
            InvalidPriceError: If prices are illogical
        """
        if direction == "LONG":
            if not (stop_loss_price < start_price < target_price):
                raise InvalidPriceError(
                    "For LONG: stop_loss < start_price < target_price",
                    {
                        "start_price": float(start_price),
                        "target_price": float(target_price),
                        "stop_loss_price": float(stop_loss_price),
                        "direction": direction,
                    }
                )
        else:  # SHORT
            if not (target_price < start_price < stop_loss_price):
                raise InvalidPriceError(
                    "For SHORT: target_price < start_price < stop_loss",
                    {
                        "start_price": float(start_price),
                        "target_price": float(target_price),
                        "stop_loss_price": float(stop_loss_price),
                        "direction": direction,
                    }
                )

