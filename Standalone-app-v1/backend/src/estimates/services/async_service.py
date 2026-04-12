import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4
import logging

from src.estimates.schemas import CreateEstimateCommand
from src.estimates.schemas.async_responses import TaskStatusResponse
from src.estimates.schemas.responses import EstimateResponse

logger = logging.getLogger(__name__)

# Very simple in-memory task registry (only for single-instance or basic dev usage)
# In production with multiple workers, this should be Redis or a similar key-value store
_TASKS_REGISTRY = {}

def create_task_entry() -> UUID:
    """Creates a new task in PENDING state and returns its ID."""
    task_id = uuid4()
    now = datetime.now(timezone.utc)
    _TASKS_REGISTRY[task_id] = {
        "task_id": task_id,
        "status": "Pending",
        "created_at": now,
        "updated_at": now,
        "error": None,
        "estimate": None,
    }
    return task_id

def get_task_status(task_id: UUID) -> TaskStatusResponse | None:
    """Gets the status of a scheduled or completed task."""
    task_data = _TASKS_REGISTRY.get(task_id)
    if not task_data:
        return None
    return TaskStatusResponse(**task_data)

async def process_async_estimate(
    task_id: UUID,
    command: CreateEstimateCommand,
    estimate_service
):
    """
    Background task that calls the synchronous-like `create_estimate` logic.
    Updates the registry at the beginning and the end of processing.
    """
    now = datetime.now(timezone.utc)
    if task_id in _TASKS_REGISTRY:
        _TASKS_REGISTRY[task_id]["status"] = "Processing"
        _TASKS_REGISTRY[task_id]["updated_at"] = now
    else:
        # Failsafe fallback
        _TASKS_REGISTRY[task_id] = {
            "task_id": task_id,
            "status": "Processing",
            "created_at": now,
            "updated_at": now,
            "error": None,
            "estimate": None,
        }

    try:
        # Small delay to mimic realism and avoid DB deadlocks if the UI polls before commit
        await asyncio.sleep(0.5)

        # Call the actual service logic
        estimate = await estimate_service.create_estimate(command)
        
        # Convert estimate domain object to Pydantic Response safely
        # We assume the service returns an Estimate SQLAlchemy model that we can parse
        parsed_estimate = EstimateResponse.model_validate(estimate)

        _TASKS_REGISTRY[task_id]["status"] = "Completed"
        _TASKS_REGISTRY[task_id]["estimate"] = parsed_estimate
        _TASKS_REGISTRY[task_id]["updated_at"] = datetime.now(timezone.utc)

        logger.info(f"Task {task_id} completed successfully for ticker {command.ticker_id}")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
        _TASKS_REGISTRY[task_id]["status"] = "Failed"
        _TASKS_REGISTRY[task_id]["error"] = str(e)
        _TASKS_REGISTRY[task_id]["updated_at"] = datetime.now(timezone.utc)
