from fastapi import APIRouter
from datetime import datetime, timezone
from src.shared.infra.config import get_settings
from src.shared.background_tasks import get_price_loop_runtime_status

router = APIRouter()

@router.get("/api/tasks/status")
async def get_tasks_status():
    settings = get_settings()
    runtime_status = get_price_loop_runtime_status()
    now_iso = datetime.now(timezone.utc).isoformat()

    return {
        "running": runtime_status["running"],
        "next_run_iso": runtime_status["next_run_iso"] or now_iso,
        "last_run_iso": runtime_status["last_run_iso"] or now_iso,
        "estimates_monitored": runtime_status["estimates_monitored"],
        "interval_seconds": getattr(settings, "PRICE_LOOP_INTERVAL_SECONDS", 60),
        "last_yahoo_call": runtime_status["last_yahoo_call"],
        "last_gdrive_sync": None
    }
