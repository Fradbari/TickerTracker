import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.estimates.domain.entities import Estimate, EstimateStatus, Direction
from src.estimates.domain.events import EstimateEvent, EstimateEventType
from pydantic import ValidationError as PydanticValidationError
from src.estimates.schemas.commands import CreateEstimateCommand, CloseEstimateCommand
from src.estimates.services.estimate_service import EstimateService
from src.estimates.services.exceptions import (
    TickerNotFoundError,
    MarketDataNotAvailableError,
    EstimateNotFoundError,
    EstimateAlreadyClosedError,
    InvalidPriceError,
)
from src.market_data.domain.entities import Ticker


@pytest.fixture
def estimate_repo_mock():
    return AsyncMock()


@pytest.fixture
def market_data_repo_mock():
    return AsyncMock()


class AsyncTransactionMock:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        pass


class AsyncSessionFactoryMock:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        pass


@pytest.fixture
def session_mock():
    session = AsyncMock()
    # Support async with session.begin():
    # session.begin() is a SYNC method returning an async context manager
    session.begin = MagicMock(return_value=AsyncTransactionMock())
    return session


@pytest.fixture
def session_factory_mock(session_mock):
    # Support async with session_factory() as session:
    factory = MagicMock()
    factory.return_value = AsyncSessionFactoryMock(session_mock)
    return factory


@pytest.fixture
def service(estimate_repo_mock, market_data_repo_mock, session_factory_mock):
    return EstimateService(
        estimate_repo=estimate_repo_mock,
        market_data_repo=market_data_repo_mock,
        session_factory=session_factory_mock,
    )


class TestEstimateServiceCreate:
    async def test_create_estimate_success_long(self, service, session_mock):
        ticker_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        # Setup mocks
        ticker_mock = MagicMock(spec=Ticker)
        ticker_mock.id = ticker_id
        
        # Mock _get_ticker internal result
        session_mock.execute.return_value.scalar_one_or_none.return_value = ticker_mock
        
        # Mock _get_current_price internal result
        latest_data_mock = MagicMock()
        latest_data_mock.close = Decimal("100.00")
        service._market_data_repo.get_latest_price.return_value = latest_data_mock
        
        cmd = CreateEstimateCommand(
            ticker_id=ticker_id,
            direction="LONG",
            target_profit_percent=Decimal("10.0"),  # target = 110.00
            stop_loss_percent=Decimal("5.0"),       # stop = 95.00
            user_id=user_id,
        )
        
        estimate = await service.create_estimate(cmd)
        
        # Verify calculates correctly
        assert estimate.start_price == Decimal("100.00")
        assert estimate.target_price == Decimal("110.00")
        assert estimate.stop_loss_price == Decimal("95.00")
        assert estimate.direction == Direction.LONG
        
        # Verify event creation in session
        # session.add should be called twice (Estimate and EstimateEvent)
        assert session_mock.add.call_count == 2
        calls = session_mock.add.call_args_list
        
        added_event = None
        for call in calls:
            obj = call[0][0]
            if isinstance(obj, EstimateEvent):
                added_event = obj
                
        assert added_event is not None
        assert added_event.event_type == EstimateEventType.CREATED
        assert added_event.estimate_id == estimate.id
        assert added_event.event_data["target_price"] == 110.0
        assert added_event.event_data["stop_loss_price"] == 95.0

    async def test_create_estimate_success_short(self, service, session_mock):
        ticker_id = uuid.uuid4()
        user_id = uuid.uuid4()
        
        ticker_mock = MagicMock(spec=Ticker)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = ticker_mock
        session_mock.execute.return_value = mock_result
        
        latest_data_mock = MagicMock()
        latest_data_mock.close = Decimal("100.00")
        service._market_data_repo.get_latest_price.return_value = latest_data_mock
        
        cmd = CreateEstimateCommand(
            ticker_id=ticker_id,
            direction="SHORT",
            target_profit_percent=Decimal("10.0"),  # target = 90.00
            stop_loss_percent=Decimal("5.0"),       # stop = 105.00
            user_id=user_id,
        )
        
        estimate = await service.create_estimate(cmd)
        
        assert estimate.start_price == Decimal("100.00")
        assert estimate.target_price == Decimal("90.00")
        assert estimate.stop_loss_price == Decimal("105.00")
        assert estimate.direction == Direction.SHORT

    async def test_create_estimate_ticker_not_found(self, service, session_mock):
        # Return None for ticker
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session_mock.execute.return_value = mock_result
        
        cmd = CreateEstimateCommand(
            ticker_id=uuid.uuid4(),
            direction="LONG",
            target_profit_percent=Decimal("10.0"),
            stop_loss_percent=Decimal("5.0"),
        )
        
        with pytest.raises(TickerNotFoundError):
            await service.create_estimate(cmd)

    async def test_create_estimate_price_not_available(self, service, session_mock):
        ticker_mock = MagicMock(spec=Ticker)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = ticker_mock
        session_mock.execute.return_value = mock_result
        
        # Return None for market price
        service._market_data_repo.get_latest_price.return_value = None
        
        cmd = CreateEstimateCommand(
            ticker_id=uuid.uuid4(),
            direction="LONG",
            target_profit_percent=Decimal("10.0"),
            stop_loss_percent=Decimal("5.0"),
        )
        
        with pytest.raises(MarketDataNotAvailableError):
            await service.create_estimate(cmd)


class TestEstimateServiceClose:
    async def test_close_estimate_success_long_win(self, service, estimate_repo_mock, session_mock):
        estimate_id = uuid.uuid4()
        
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        mock_estimate.start_price = Decimal("100.00")
        mock_estimate.direction = Direction.LONG
        mock_estimate.id = estimate_id
        
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        session_mock.merge.return_value = mock_estimate
        
        cmd = CloseEstimateCommand(
            estimate_id=estimate_id,
            exit_price=Decimal("110.00"),
            reason="Manual close",
            user_id=uuid.uuid4(),
        )
        
        est = await service.close_estimate(cmd)
        
        assert est.exit_price == Decimal("110.00")
        assert est.realized_pnl == Decimal("10.00") # LONG Win
        assert est.status == EstimateStatus.CLOSED_WIN
        
        # Check event
        session_mock.add.assert_called_once()
        added_event = session_mock.add.call_args[0][0]
        assert isinstance(added_event, EstimateEvent)
        assert added_event.event_type == EstimateEventType.CLOSED
        assert added_event.event_data["realized_pnl"] == 10.0
        assert added_event.event_data["final_status"] == EstimateStatus.CLOSED_WIN.value

    async def test_close_estimate_success_short_win(self, service, estimate_repo_mock, session_mock):
        estimate_id = uuid.uuid4()
        
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        mock_estimate.start_price = Decimal("100.00")
        mock_estimate.direction = Direction.SHORT
        mock_estimate.id = estimate_id
        
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        session_mock.merge.return_value = mock_estimate
        
        cmd = CloseEstimateCommand(
            estimate_id=estimate_id,
            exit_price=Decimal("90.00"),
            reason="Manual close",
            user_id=uuid.uuid4(),
        )
        
        est = await service.close_estimate(cmd)
        
        assert est.exit_price == Decimal("90.00")
        assert est.realized_pnl == Decimal("10.00") # SHORT Win: 100 - 90
        assert est.status == EstimateStatus.CLOSED_WIN

    async def test_close_estimate_not_found(self, service, estimate_repo_mock):
        estimate_repo_mock.get_by_id.return_value = None
        
        cmd = CloseEstimateCommand(estimate_id=uuid.uuid4(), exit_price=Decimal("110.00"), reason="test")
        
        with pytest.raises(EstimateNotFoundError):
            await service.close_estimate(cmd)

    async def test_close_estimate_already_closed(self, service, estimate_repo_mock):
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.CLOSED_WIN
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        
        cmd = CloseEstimateCommand(estimate_id=uuid.uuid4(), exit_price=Decimal("110.00"), reason="test")
        
        with pytest.raises(EstimateAlreadyClosedError):
            await service.close_estimate(cmd)

    async def test_close_estimate_invalid_price(self, service, estimate_repo_mock):
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        
        with pytest.raises(PydanticValidationError):
            CloseEstimateCommand(estimate_id=uuid.uuid4(), exit_price=Decimal("-10.00"), reason="test")


class TestEstimateServiceCheckTargets:
    async def test_check_targets_long_target_hit(self, service, estimate_repo_mock, session_mock):
        estimate_id = uuid.uuid4()
        
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        mock_estimate.direction = Direction.LONG
        mock_estimate.start_price = Decimal("100.00")
        mock_estimate.target_price = Decimal("110.00")
        mock_estimate.stop_loss_price = Decimal("90.00")
        mock_estimate.id = estimate_id
        
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        session_mock.merge.return_value = mock_estimate
        
        est = await service.check_and_update_targets(estimate_id, current_price=Decimal("115.00"))
        
        assert est is not None
        assert est.status == EstimateStatus.CLOSED_WIN
        assert est.exit_price == Decimal("115.00")
        assert est.realized_pnl == Decimal("15.00")
        
        # 2 events added: TARGET_HIT and CLOSED
        assert session_mock.add.call_count == 2

    async def test_check_targets_long_stop_hit(self, service, estimate_repo_mock, session_mock):
        estimate_id = uuid.uuid4()
        
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        mock_estimate.direction = Direction.LONG
        mock_estimate.start_price = Decimal("100.00")
        mock_estimate.target_price = Decimal("110.00")
        mock_estimate.stop_loss_price = Decimal("90.00")
        mock_estimate.id = estimate_id
        
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        session_mock.merge.return_value = mock_estimate
        
        est = await service.check_and_update_targets(estimate_id, current_price=Decimal("85.00"))
        
        assert est is not None
        assert est.status == EstimateStatus.CLOSED_LOSS
        assert est.exit_price == Decimal("85.00")
        assert est.realized_pnl == Decimal("-15.00")

    async def test_check_targets_no_hit(self, service, estimate_repo_mock):
        estimate_id = uuid.uuid4()
        
        mock_estimate = MagicMock(spec=Estimate)
        mock_estimate.status = EstimateStatus.OPEN
        mock_estimate.direction = Direction.LONG
        mock_estimate.start_price = Decimal("100.00")
        mock_estimate.target_price = Decimal("110.00")
        mock_estimate.stop_loss_price = Decimal("90.00")
        mock_estimate.id = estimate_id
        
        estimate_repo_mock.get_by_id.return_value = mock_estimate
        
        est = await service.check_and_update_targets(estimate_id, current_price=Decimal("105.00"))
        
        assert est is None  # no hit

    async def test_check_targets_not_found(self, service, estimate_repo_mock):
        estimate_repo_mock.get_by_id.return_value = None
        with pytest.raises(EstimateNotFoundError):
            await service.check_and_update_targets(uuid.uuid4(), Decimal("100"))
