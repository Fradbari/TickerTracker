"""
API Routes for Estimates endpoints.

This module defines REST API endpoints for managing estimates,
following the ApiResponse wrapper pattern and dependency injection.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, Request, Response, BackgroundTasks, status
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
from src.estimates.schemas.async_responses import TaskStatusResponse
from src.estimates.services.estimate_history_service import EstimateHistoryService
from src.estimates.services.estimate_service import EstimateService
from src.estimates.services.async_service import get_task_status, create_task_entry, process_async_estimate
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
# Dependencies
# ============================================================================

def get_estimate_repository(session: AsyncSession = Depends(get_db)) -> EstimateRepository:
    return EstimateRepository(session)


def get_market_data_repository(session: AsyncSession = Depends(get_db)) -> MarketDataRepository:
    return MarketDataRepository(session)


def get_estimate_event_repository(session: AsyncSession = Depends(get_db)) -> EstimateEventRepository:
    return EstimateEventRepository(session)


def get_estimate_service(
    estimate_repo: EstimateRepository = Depends(get_estimate_repository),
    market_data_repo: MarketDataRepository = Depends(get_market_data_repository),
    event_repo: EstimateEventRepository = Depends(get_estimate_event_repository),
    session: AsyncSession = Depends(get_db)
) -> EstimateService:
    # EstimateService requires a session_factory callable to manage transactions
    return EstimateService(
        estimate_repo=estimate_repo,
        market_data_repo=market_data_repo,
        event_repo=event_repo,
        session_factory=lambda: get_db()
    )


def get_history_service(
    event_repo: EstimateEventRepository = Depends(get_estimate_event_repository),
) -> EstimateHistoryService:
    return EstimateHistoryService(event_repo)


# ============================================================================
# Routes
# ============================================================================

@router.get(
    "/tasks/{task_id}",
    response_model=ApiResponse[TaskStatusResponse],
    summary="Get Async Task Status",
    description="Check the current status of an async estimate creation task."
)
async def get_estimate_task_status(
    task_id: UUID,
) -> dict:
    """Get the status of an estimate async task."""
    status_response = get_task_status(task_id)
    if not status_response:
        return error_response(
            message="Task not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="TASK_NOT_FOUND"
        )
    return success_response(
        data=status_response.model_dump(),
        message="Task status retrieved successfully"
    )


@router.post(
    "/async",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ApiResponse[dict],
    summary="Create Estimate Asynchronously",
    description="Submits an estimate creation request to be processed in the background."
)
async def create_estimate_async(
    command: CreateEstimateCommand,
    background_tasks: BackgroundTasks,
    request: Request,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Launch async task for estimate creation."""
    # Create the task entry immediately
    task_id = create_task_entry()
    
    # Schedule the actual task in background
    background_tasks.add_task(
        process_async_estimate,
        task_id=task_id,
        command=command,
        estimate_service=estimate_service
    )
    
    return success_response(
        data={"task_id": str(task_id), "status": "Pending"},
        message="Estimate creation accepted and processing in background",
        status_code=status.HTTP_202_ACCEPTED
    )


@router.get(
    "",
    response_model=ApiResponse[EstimateListResponse],
    summary="List Estimates",
    description="Retrieve a paginated list of estimates with optional filtering."
)
@limiter.limit("60/minute", exempt_when=is_whitelisted)
async def list_estimates(
    request: Request,
    # Pagination
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: str | None = Query(None, description="Cursor for next page"),
    # Filters
    ticker_id: UUID | None = Query(None, description="Filter by ticker UUID"),
    status: str | None = Query(None, description="Filter by status (OPEN, CLOSED_WIN, etc.)"),
    direction: str | None = Query(None, description="Filter by direction (LONG, SHORT)"),
    ai_model: str | None = Query(None, description="Filter by AI model"),
    has_ai_analysis: bool | None = Query(None, description="Filter estimates with AI reasoning"),
    is_active: bool | None = Query(None, description="Filter currently active (OPEN) estimates"),
    # Services
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Get localized, paginated list of estimates."""
    filters = EstimateFilters(
        ticker_id=ticker_id,
        status=status,
        direction=direction,
        ai_model=ai_model,
        has_ai_analysis=has_ai_analysis,
        is_active=is_active,
    )
    
    pagination = Pagination(limit=limit, cursor=cursor)
    
    # Call service
    result = await estimate_service.get_estimates(filters, pagination)
    
    response_data = EstimateListResponse(
        items=[EstimateResponse.model_validate(e) for e in result.items],
        total=result.total,
        page_info=result.page_info.model_dump(),
    )
    
    return success_response(
        data=response_data.model_dump(),
        message="Estimates retrieved successfully"
    )


@router.get(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateResponse],
    summary="Get Estimate",
    description="Retrieve detailed information about a specific estimate.",
)
async def get_estimate(
    estimate_id: UUID,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Get single estimate by ID."""
    try:
        estimate = await estimate_service.get_estimate_by_id(estimate_id)
        return success_response(
            data=EstimateResponse.model_validate(estimate).model_dump(),
            message="Estimate retrieved successfully"
        )
    except EstimateNotFoundError:
        return error_response(
            message=f"Estimate with ID {estimate_id} not found",
            status_code=404,
            error_code="ESTIMATE_NOT_FOUND"
        )


@router.post(
    "",
    status_code=201,
    response_model=ApiResponse[EstimateCreatedResponse],
    summary="Create Estimate",
    description="Create a new estimate synchronously.",
)
async def create_estimate(
    command: CreateEstimateCommand,
    request: Request,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Synchronous creation logic currently retained for backwards compatibility."""
    try:
        # If user_id wasn't in command but is in request state (from auth middleware)
        if getattr(request.state, "user", None) and command.user_id is None:
            command.user_id = request.state.user.id
            
        estimate = await estimate_service.create_estimate(command)
        
        response_data = EstimateCreatedResponse(
            estimate=EstimateResponse.model_validate(estimate),
            message="Estimate created successfully"
        )
        
        return success_response(
            data=response_data.model_dump(),
            message="Estimate created successfully",
            status_code=201
        )
        
    except TickerNotFoundError as e:
        return error_response(message=str(e), status_code=404, error_code="TICKER_NOT_FOUND")
    except MarketDataNotAvailableError as e:
        return error_response(message=str(e), status_code=400, error_code="MARKET_DATA_UNAVAILABLE")
    except InvalidPriceError as e:
        return error_response(message=str(e), status_code=400, error_code="INVALID_PRICE")
    except ValueError as e:
        return error_response(message=str(e), status_code=400, error_code="VALIDATION_ERROR")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(message=f"Unexpected error: {str(e)}", status_code=500, error_code="INTERNAL_SERVER_ERROR")


@router.patch(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateUpdatedResponse],
    summary="Update Estimate",
    description="Update mutable fields of an open estimate."
)
async def update_estimate(
    estimate_id: UUID,
    command: UpdateEstimateCommand,
    request: Request,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Update estimate details."""
    try:
        # Ensure command ID matches path param
        command.estimate_id = estimate_id
        
        # Add user_id from context if available
        if getattr(request.state, "user", None) and command.user_id is None:
            command.user_id = request.state.user.id
            
        estimate = await estimate_service.update_estimate(command)
        
        response_data = EstimateUpdatedResponse(
            estimate=EstimateResponse.model_validate(estimate),
            message="Estimate updated successfully"
        )
        
        return success_response(
            data=response_data.model_dump(),
            message="Estimate updated successfully"
        )
        
    except EstimateNotFoundError as e:
        return error_response(message=str(e), status_code=404, error_code="ESTIMATE_NOT_FOUND")
    except InvalidEstimateStateError as e:
        return error_response(message=str(e), status_code=400, error_code="INVALID_STATE")
    except ValueError as e:
        return error_response(message=str(e), status_code=400, error_code="VALIDATION_ERROR")


@router.post(
    "/{estimate_id}/close",
    response_model=ApiResponse[EstimateResponse],
    summary="Close Estimate",
    description="Manually close an estimate with an exit price."
)
async def close_estimate(
    estimate_id: UUID,
    command: CloseEstimateCommand,
    request: Request,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Close an estimate manually."""
    try:
        # Ensure command matches path
        command.estimate_id = estimate_id
        
        # Add user_id from context if available
        if getattr(request.state, "user", None) and command.user_id is None:
            command.user_id = request.state.user.id
            
        estimate = await estimate_service.close_estimate(command)
        
        return success_response(
            data=EstimateResponse.model_validate(estimate).model_dump(),
            message="Estimate closed successfully"
        )
        
    except EstimateNotFoundError as e:
        return error_response(message=str(e), status_code=404, error_code="ESTIMATE_NOT_FOUND")
    except EstimateAlreadyClosedError as e:
        return error_response(message=str(e), status_code=400, error_code="ALREADY_CLOSED")
    except InvalidPriceError as e:
        return error_response(message=str(e), status_code=400, error_code="INVALID_PRICE")
    except Exception as e:
        return error_response(message=str(e), status_code=400, error_code="BAD_REQUEST")


@router.delete(
    "/{estimate_id}",
    response_model=ApiResponse[EstimateDeletedResponse],
    summary="Delete Estimate",
    description="Soft-delete an estimate (moves it to deleted state rather than hard removal)."
)
async def delete_estimate(
    estimate_id: UUID,
    request: Request,
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Soft-delete an estimate."""
    try:
        user_id = None
        if getattr(request.state, "user", None):
            user_id = request.state.user.id
            
        estimate = await estimate_service.delete_estimate(estimate_id, user_id=user_id)
        
        response_data = EstimateDeletedResponse(
            id=estimate_id,
            status=str(estimate.status.name) if hasattr(estimate.status, 'name') else str(estimate.status),
            message="Estimate securely marked as deleted"
        )
        
        return success_response(
            data=response_data.model_dump(),
            message="Estimate deleted successfully"
        )
        
    except EstimateNotFoundError as e:
        return error_response(message=str(e), status_code=404, error_code="ESTIMATE_NOT_FOUND")


@router.get(
    "/{estimate_id}/history",
    response_model=ApiResponse[EstimateHistoryResponse],
    summary="Get Estimate History",
    description="Get full audit trail of all changes and events for an estimate."
)
async def get_estimate_history(
    estimate_id: UUID,
    history_service: EstimateHistoryService = Depends(get_history_service),
    estimate_service: EstimateService = Depends(get_estimate_service),
) -> dict:
    """Get audit trail history for an estimate."""
    try:
        # First ensure the estimate exists
        await estimate_service.get_estimate_by_id(estimate_id)
        
        # Then get its history
        snapshot = await history_service.get_estimate_snapshot(estimate_id)
        
        response_data = EstimateHistoryResponse(
            estimate_id=estimate_id,
            audit_trail=[entry.model_dump() for entry in snapshot.audit_trail],
            summary=snapshot.summary.model_dump(),
        )
        
        return success_response(
            data=response_data.model_dump(),
            message="Estimate history retrieved successfully"
        )
        
    except EstimateNotFoundError as e:
        return error_response(message=str(e), status_code=404, error_code="ESTIMATE_NOT_FOUND")
