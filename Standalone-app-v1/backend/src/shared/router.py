from fastapi import APIRouter
from datetime import datetime, timezone
from src.shared.infra.config import get_settings

router = APIRouter()

@router.get("/api/tasks/status")
async def get_tasks_status():
    settings = get_settings()
    return {
        "running": True,
        "next_run_iso": datetime.now(timezone.utc).isoformat(),
        "last_run_iso": datetime.now(timezone.utc).isoformat(),
        "estimates_monitored": 0,
        "interval_seconds": getattr(settings, "PRICE_LOOP_INTERVAL_SECONDS", 60),
        "last_yahoo_call": {"timestamp": datetime.now(timezone.utc).isoformat(), "success": True},
        "last_gdrive_sync": None
    }
