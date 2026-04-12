"""
API Routes for Estimates endpoints.

This module defines REST API endpoints for managing estimates,
following the ApiResponse wrapper pattern and dependency injection.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.estimates.repositories.estimate_event_repository import EstimateEventRepository
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.estimates.schemas import (
    CloseEstimateCommand,
    CreateEstimateCommand,
    EstimateCreatedResponse,
    EstimateDeletedResponse,
    EstimateFilters,
    EstimateHistoryResponse,
    EstimateListResponse,
    EstimateResponse,
    EstimateUpdatedResponse,
    UpdateEstimateCommand,
)
from src.estimates.services.estimate_history_service import EstimateHistoryService
from src.estimates.services.estimate_service import EstimateService
from src.estimates.services.exceptions import (
    EstimateAlreadyClosedError,
    EstimateNotFoundError,
    InvalidEstimateStateError,
    InvalidPriceError,
    MarketDataNotAvailableError,
    TickerNotFoundError,
)
from src.infra.security.rate_limit import is_whitelisted, limiter
from src.market_data.repositories.market_data_repository import MarketDataRepository
from src.shared.infra.database import get_db
from src.shared.schemas.api_response import ApiResponse, error_response, success_response
from src.shared.schemas.pagination import Pagination

# Router configuration
router = APIRouter(
    prefix="/api/estimates",
    tags=["estimates"],
)


# ============================================================================
# DEPENDENCY INJECTION FACTORIES
# ============================================================================

async def get_estimate_service(
    db: AsyncSession = Depends(get_db),
) -> EstimateService:
    """
    Dependency injection factory for EstimateService.

    Creates service instance with repository dependencies injected.
    Uses the provided database session for transactional operations.
    """
    from src.shared.infra.database import AsyncSessionLocal

    estimate_repo = EstimateRepository(AsyncSessionLocal)
    market_data_repo = MarketDataRepository(AsyncSessionLocal)

    return EstimateService(
        estimate_repo=estimate_repo,
        market_data_repo=market_data_repo,
        session_factory=AsyncSessionLocal,
    )


async def get_estimate_history_service(
    db: AsyncSession = Depends(get_db),
) -> EstimateHistoryService:
    """
    Dependency injection factory for EstimateHistoryService.

    Creates history service instance with repository dependencies.
    """
    from src.shared.infra.database import AsyncSessionLocal

    estimate_repo = EstimateRepository(AsyncSessionLocal)
    event_repo = EstimateEventRepository(AsyncSessionLocal)

    return EstimateHistoryService(
        estimate_repo=estimate_repo,
        event_repo=event_repo,
        session_factory=AsyncSessionLocal,
    )


async def get_estimate_repository(
    db: AsyncSession = Depends(get_db),
) -> EstimateRepository:
    """
    Dependency injection factory for EstimateRepository.

    Used for read-only operations that don't require service orchestration.
    """
    from src.shared.infra.database import AsyncSessionLocal

    return EstimateRepository(AsyncSessionLocal)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=ApiResponse[EstimateCreatedResponse],
    status_code=201,
    summary="Create new estimate",
    description="""
    Create a new estimate for a ticker with AI-generated or user-defined parameters.

    The service will:
    1. Validate ticker exists
    2. Fetch current market price
    3. Calculate target and stop-loss prices from percentages
    4. Create estimate entity with OPEN status
    5. Publish ESTIMATE_CREATED domain event

    Returns the created estimate with calculated prices.
    """,
    responses={
        201: {
            "description": "Estimate created successfully",
            "content": {"application/json": {"example": {"data": {"estimate": {"id": "123e4567-e89b-12d3-a456-426614174000", "ticker_id": "987e6543-e21b-34c5-b678-526614174000", "status": "OPEN", "trigger_price": 150.0, "target_price": 165.0, "stop_loss_price": 135.0}, "message": "Estimate created successfully"}, "meta": {"correlation_id": "abc"}}}},
        },
        400: {
            "description": "Invalid input - Ticker not found, invalid price, etc.",
            "content": {"application/json": {"example": {"error": {"code": "invalid_request", "message": "Ticker not found"}}}},
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {"example": {"error": {"code": "internal_error", "message": "Failed to fetch market data"}}}},
        }
    }
)
@limiter.limit("30/minute", exempt_when=is_whitelisted)
async def create_estimate(
    request: Request,
    response: Response,
    command: CreateEstimateCommand,
    service: EstimateService = Depends(get_estimate_service),
) -> ApiResponse[EstimateCreatedResponse]:
    """
    Create a new estimate.

    Args:
        command: CreateEstimateCommand with ticker_id, percentages, direction
        service: Injected EstimateService

    Returns:
        ApiResponse wrapping EstimateCreatedResponse with created estimate

    Raises:
        400: Invalid input (ticker not found, invalid percentages, etc.)
        500: Internal server error
    """
    trace_id = str(uuid4())

    try:
        estimate = await service.create_estimate(command)

        response_data = EstimateCreatedResponse(
            estimate=EstimateResponse.model_validate(estimate),
            message="Estimate created successfully",
        )

        return success_response(data=response_data, trace_id=trace_id)

    except TickerNotFoundError as e:
        return error_response(
            code="TICKER_NOT_FOUND",
            message=str(e),
            details={"ticker_id": str(command.ticker_id)},
            trace_id=trace_id,
        )
    except MarketDataNotAvailableError as e:
        return error_response(
            code="MARKET_DATA_UNAVAILABLE",
            message=str(e),
            details={"ticker_id": str(command.ticker_id)},
            trace_id=trace_id,
        )
    except InvalidPriceError as e:
        return error_response(
            code="INVALID_PRICE",
            message=str(e),
            trace_id=trace_id,
        )
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed with exception: {repr(e)}",
            trace_id=trace_id,
        )


@router.get(
    "",
    response_model=ApiResponse[EstimateListResponse],
    summary="List estimates with filters and pagination",
    description="""
    Retrieve a paginated list of estimates with optional filters.

    Supports filtering by:
    - ticker_id: Filter by specific ticker
    - user_id: Filter by user
    - status: Filter by estimate status (OPEN, CLOSED_WIN, etc.)
    - direction: Filter by trade direction (LONG, SHORT)
    - created_after / created_before: Date range filter
    - include_deleted: Include soft-deleted estimates

    Returns paginated results with cursor-based navigation.
    """,
    response_description="A paginated list of estimates",
    responses={
        200: {
            "description": "Estimates retrieved successfully",
            "content": {"application/json": {"example": {"data": {"items": [{"id": "123", "ticker_id": "456", "status": "OPEN", "trigger_price": 100.0}], "total": 1, "page_info": {"has_next_page": False, "next_cursor": None}}, "meta": {"correlation_id": "abc"}}}}
        },
        500: {
            "description": "Internal server error",
            "content": {"application/json": {"example": {"error": {"code": "INTERNAL_ERROR", "message": "Failed to list estimates"}}}}
        }
    }
)
async def list_estimates(
    ticker_id: UUID | None = Query(None, description="Filter by ticker ID"),
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    status: str | None = Query(None, description="Filter by status"),
    direction: str | None = Query(None, description="Filter by direction (LONG/SHORT)"),
    include_deleted: bool = Query(False, description="Include soft-deleted estimates"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: str | None = Query(None, description="Pagination cursor"),
    repository: EstimateRepository = Depends(get_estimate_repository),
) -> ApiResponse[EstimateListResponse]:
    """
    List estimates with filters and pagination.

    Args:
        ticker_id: Optional ticker ID filter
        user_id: Optional user ID filter
        status: Optional status filter
        direction: Optional direction filter
        include_deleted: Whether to include deleted estimates
        limit: Items per page (1-100)
        cursor: Pagination cursor for next page
        repository: Injected EstimateRepository

    Returns:
        ApiResponse wrapping EstimateListResponse with paginated estimates
    """
    trace_id = str(uuid4())

    try:
        # Build filters
        filters = EstimateFilters(
            ticker_id=ticker_id,
            user_id=user_id,
            status=status,
            direction=direction,
            include_deleted=include_deleted,
        )

        # Build pagination
        pagination = Pagination(limit=limit, cursor=cursor)

        # Query repository
        result = await repository.get_all(filters, pagination)

        # Convert to response DTOs
        estimate_responses = [
            EstimateResponse.model_validate(estimate)
            for estimate in result.items
        ]

        response_data = EstimateListResponse(
            items=estimate_responses,
            total=len(estimate_responses),
            page_info={
                "has_next_page": result.page_info.has_next_page,
                "has_previous_page": result.page_info.has_previous_page,
                "next_cursor": result.page_info.next_cursor,
                "previous_cursor": result.page_info.previous_cursor,
            },
        )

        return success_response(data=response_data, trace_id=trace_id)

    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed to list estimates: {str(e)}",
            trace_id=trace_id,
        )


@router.get(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateResponse],
    summary="Get estimate by ID",
    description="""
    Retrieve detailed information about a specific estimate.

    Returns all estimate fields including calculated prices, AI metadata,
    timestamps, and exit data (if estimate is closed).
    """,
    response_description="Estimate details",
    responses={
        200: {
            "description": "Estimate found",
            "content": {"application/json": {"example": {"data": {"id": "123", "ticker_id": "456", "status": "OPEN", "trigger_price": 100.0}, "meta": {}}}}
        },
        404: {
            "description": "Estimate not found",
            "content": {"application/json": {"example": {"error": {"code": "ESTIMATE_NOT_FOUND", "message": "Estimate with ID 123 not found"}}}}
        },
        422: {
            "description": "Validation Error - Invalid UUID",
            "content": {"application/json": {"example": {"detail": [{"loc": ["path", "estimate_id"], "msg": "value is not a valid uuid"}]}}}
        }
    }
)
async def get_estimate(
    estimate_id: UUID,
    repository: EstimateRepository = Depends(get_estimate_repository),
) -> ApiResponse[EstimateResponse]:
    """
    Get estimate by ID.

    Args:
        estimate_id: UUID of the estimate
        repository: Injected EstimateRepository

    Returns:
        ApiResponse wrapping EstimateResponse with estimate details

    Raises:
        404: Estimate not found
    """
    trace_id = str(uuid4())

    try:
        estimate = await repository.get_by_id(estimate_id)

        if not estimate:
            return error_response(
                code="ESTIMATE_NOT_FOUND",
                message=f"Estimate with ID {estimate_id} not found",
                details={"estimate_id": str(estimate_id)},
                trace_id=trace_id,
            )

        response_data = EstimateResponse.model_validate(estimate)

        return success_response(data=response_data, trace_id=trace_id)

    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed with exception: {repr(e)}",
            trace_id=trace_id,
        )


@router.patch(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateUpdatedResponse],
    summary="Update estimate",
    description="""
    Update an existing estimate's parameters.

    Allows updating:
    - Target profit percentage
    - Stop loss percentage
    - AI metadata (model, confidence, reasoning)

    The service will recalculate target_price and stop_loss_price based on
    new percentages and current start_price.

    Publishes ESTIMATE_UPDATED domain event.
    """,
    responses={
        200: {
            "description": "Estimate successfully updated",
            "content": {"application/json": {"example": {"data": {"estimate": {"id": "123", "target_price": 110.0, "status": "OPEN"}, "message": "Estimate updated successfully"}, "meta": {}}}}
        },
        400: {
            "description": "Invalid parameters or status",
            "content": {"application/json": {"example": {"error": {"code": "INVALID_PRICE", "message": "Target price must be greater than current price"}}}}
        },
        404: {
            "description": "Estimate not found",
            "content": {"application/json": {"example": {"error": {"code": "ESTIMATE_NOT_FOUND", "message": "Estimate 123 not found"}}}}
        },
        422: {
            "description": "Validation Error - Invalid body/UUID",
            "content": {"application/json": {"example": {"detail": [{"loc": ["body", "target_percentage"], "msg": "Input should be greater than 0"}]}}}
        }
    }
)
async def update_estimate(
    estimate_id: UUID,
    command: UpdateEstimateCommand,
    service: EstimateService = Depends(get_estimate_service),
) -> ApiResponse[EstimateUpdatedResponse]:
    """
    Update an estimate.

    Args:
        estimate_id: UUID of the estimate to update
        command: UpdateEstimateCommand with new values
        service: Injected EstimateService

    Returns:
        ApiResponse wrapping EstimateUpdatedResponse with updated estimate

    Raises:
        404: Estimate not found
        400: Invalid state or parameters
    """
    trace_id = str(uuid4())

    try:
        # Set estimate_id in command
        command.estimate_id = estimate_id
        estimate = await service.update_estimate(command)

        response_data = EstimateUpdatedResponse(
            estimate=EstimateResponse.model_validate(estimate),
            message="Estimate updated successfully",
        )

        return success_response(data=response_data, trace_id=trace_id)

    except EstimateNotFoundError as e:
        return error_response(
            code="ESTIMATE_NOT_FOUND",
            message=str(e),
            details={"estimate_id": str(estimate_id)},
            trace_id=trace_id,
        )
    except EstimateAlreadyClosedError as e:
        return error_response(
            code="ESTIMATE_ALREADY_CLOSED",
            message=str(e),
            details={"estimate_id": str(estimate_id)},
            trace_id=trace_id,
        )
    except InvalidPriceError as e:
        return error_response(
            code="INVALID_PRICE",
            message=str(e),
            trace_id=trace_id,
        )
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed to update estimate: {str(e)}",
            trace_id=trace_id,
        )


@router.delete(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateDeletedResponse],
    summary="Close estimate",
    description="""
    Close an estimate with specified exit price and status.

    This endpoint performs a logical close (not deletion). The estimate:
    - Status changes to CLOSED_WIN, CLOSED_LOSS, or CLOSED_MANUAL
    - Exit price and realized PnL are calculated
    - closed_at timestamp is set
    - Estimate remains in database (soft delete)

    Publishes ESTIMATE_CLOSED domain event.
    """,
    responses={
        200: {
            "description": "Estimate closed successfully",
            "content": {"application/json": {"example": {"data": {"id": "123", "status": "CLOSED_WIN", "message": "Estimate closed successfully with status CLOSED_WIN"}, "meta": {}}}}
        },
        400: {
            "description": "Estimate already closed or invalid state",
            "content": {"application/json": {"example": {"error": {"code": "ESTIMATE_ALREADY_CLOSED", "message": "Estimate is already closed"}}}}
        },
        404: {
            "description": "Estimate not found",
            "content": {"application/json": {"example": {"error": {"code": "ESTIMATE_NOT_FOUND", "message": "Estimate 123 not found"}}}}
        },
        422: {
            "description": "Validation Error",
            "content": {"application/json": {"example": {"detail": [{"loc": ["body", "exit_price"], "msg": "Field required"}]}}}
        }
    }
)
async def close_estimate(
    estimate_id: UUID,
    command: CloseEstimateCommand,
    service: EstimateService = Depends(get_estimate_service),
) -> ApiResponse[EstimateDeletedResponse]:
    """
    Close an estimate (logical delete).

    Args:
        estimate_id: UUID of the estimate to close
        command: CloseEstimateCommand with exit_price and final_status
        service: Injected EstimateService

    Returns:
        ApiResponse wrapping EstimateDeletedResponse with closure confirmation

    Raises:
        404: Estimate not found
        400: Estimate already closed or invalid state
    """
    trace_id = str(uuid4())

    try:
        # Set estimate_id in command
        command.estimate_id = estimate_id
        estimate = await service.close_estimate(command)

        response_data = EstimateDeletedResponse(
            id=estimate.id,
            status=estimate.status.value,
            message=f"Estimate closed successfully with status {estimate.status.value}",
        )

        return success_response(data=response_data, trace_id=trace_id)

    except EstimateNotFoundError as e:
        return error_response(
            code="ESTIMATE_NOT_FOUND",
            message=str(e),
            details={"estimate_id": str(estimate_id)},
            trace_id=trace_id,
        )
    except EstimateAlreadyClosedError as e:
        return error_response(
            code="ESTIMATE_ALREADY_CLOSED",
            message=str(e),
            details={"estimate_id": str(estimate_id)},
            trace_id=trace_id,
        )
    except InvalidEstimateStateError as e:
        return error_response(
            code="INVALID_ESTIMATE_STATE",
            message=str(e),
            trace_id=trace_id,
        )
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed to close estimate: {str(e)}",
            trace_id=trace_id,
        )


@router.get(
    "/{estimate_id}/history",
    response_model=ApiResponse[EstimateHistoryResponse],
    summary="Get estimate audit trail",
    description="""
    Retrieve complete audit trail for an estimate.

    Returns chronological history of all events:
    - CREATED: Initial creation
    - UPDATED: Parameter changes
    - TARGET_HIT / STOP_LOSS_HIT: Automated closes
    - CLOSED: Manual closure

    Each event includes:
    - Event type and timestamp
    - User who triggered the event
    - Changed fields with before/after values
    - Human-readable description

    Also includes summary statistics:
    - Total number of events
    - First and last event timestamps
    - Current estimate state
    """,
    responses={
        200: {
            "description": "Audit trail retrieved successfully",
            "content": {"application/json": {"example": {"data": {"events": [{"event_type": "CREATED", "timestamp": "2023-10-27T10:00:00Z"}], "summary": {"total_events": 1}}, "meta": {}}}}
        },
        404: {
            "description": "Estimate not found",
            "content": {"application/json": {"example": {"error": {"code": "ESTIMATE_NOT_FOUND", "message": "Estimate 123 not found"}}}}
        },
        422: {
            "description": "Validation Error - Invalid UUID",
            "content": {"application/json": {"example": {"detail": [{"loc": ["path", "estimate_id"], "msg": "value is not a valid uuid"}]}}}
        }
    }
)
async def get_estimate_history(
    estimate_id: UUID,
    history_service: EstimateHistoryService = Depends(get_estimate_history_service),
) -> ApiResponse[EstimateHistoryResponse]:
    """
    Get complete audit trail for an estimate.

    Args:
        estimate_id: UUID of the estimate
        history_service: Injected EstimateHistoryService

    Returns:
        ApiResponse wrapping EstimateHistoryResponse with audit trail

    Raises:
        404: Estimate not found
    """
    trace_id = str(uuid4())

    try:
        # Get audit trail
        audit_entries = await history_service.get_audit_trail(estimate_id)

        # Get summary
        summary = await history_service.get_history_summary(estimate_id)

        # Convert to response format
        audit_list = [
            {
                "event_id": str(entry.event_id),
                "event_type": entry.event_type,
                "timestamp": entry.timestamp.isoformat(),
                "user_id": str(entry.user_id) if entry.user_id else None,
                "description": entry.description,
                "changes": [
                    {
                        "field": change.field,
                        "old_value": str(change.old_value) if change.old_value is not None else None,
                        "new_value": str(change.new_value) if change.new_value is not None else None,
                    }
                    for change in entry.changes
                ],
            }
            for entry in audit_entries
        ]

        summary_dict = {
            "total_events": summary.total_events,
            "first_event_at": summary.first_event_at.isoformat(),
            "last_event_at": summary.last_event_at.isoformat(),
            "event_type_counts": summary.event_type_counts,
        }

        response_data = EstimateHistoryResponse(
            estimate_id=estimate_id,
            audit_trail=audit_list,
            summary=summary_dict,
        )

        return success_response(data=response_data, trace_id=trace_id)

    except EstimateNotFoundError as e:
        return error_response(
            code="ESTIMATE_NOT_FOUND",
            message=str(e),
            details={"estimate_id": str(estimate_id)},
            trace_id=trace_id,
        )
    except Exception as e:
        return error_response(
            code="INTERNAL_ERROR",
            message=f"Failed to get estimate history: {str(e)}",
            trace_id=trace_id,
        )

@router.get(
    "/statistics/backend-check",
    response_model=ApiResponse[dict],
    summary="Get temporary backend check statistics",
    description="Returns backend statistics to verify Target Evaluation and History Sync jobs.",
    tags=["Testing & Internal"]
)
async def get_backend_statistics(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """
    Temporary endpoint to get counts from DB to visualize in Dashboard.
    """
    import logging
    logger = logging.getLogger("estimates.api")
    trace_id = getattr(request.state, "trace_id", "local")

    try:

        from sqlalchemy import func, select

        from src.estimates.domain.entities import Estimate, EstimateStatus
        from src.market_data.domain.market_data import MarketData

        # Open Estimates Count
        stmt_open = select(func.count(Estimate.id)).where(Estimate.status == EstimateStatus.OPEN)
        open_count = (await session.execute(stmt_open)).scalar() or 0

        # Closed by Engine count (closed recently)
        stmt_closed = select(func.count(Estimate.id)).where(Estimate.status.in_([
            EstimateStatus.CLOSED_WIN,
            EstimateStatus.CLOSED_LOSS,
            EstimateStatus.EXPIRED
        ]))
        closed_count = (await session.execute(stmt_closed)).scalar() or 0

        # Synced History rows length
        stmt_market = select(func.count(MarketData.ticker_id))
        market_rows = (await session.execute(stmt_market)).scalar() or 0

        return success_response(
            data={
                "open_estimates": open_count,
                "auto_closed_estimates": closed_count,
                "synced_market_rows": market_rows,
                "backend_jobs_active": True
            },
            trace_id=trace_id
        )
    except Exception as e:
        logger.error(f"Failed to fetch backend statistics: {e}")
        return error_response(
            code="INTERNAL_ERROR",
            message="Failed fetching stats",
            trace_id=trace_id
        )

