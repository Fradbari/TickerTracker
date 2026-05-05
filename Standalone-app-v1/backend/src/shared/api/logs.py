import json
import os
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.shared.schemas.api_response import success_response

router = APIRouter(prefix='/api/logs', tags=['Logs'])
logger = structlog.get_logger(__name__)
LOG_FILE_PATH = '/app/logs/app.log'


class FrontendLogIn(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: Literal["info", "warn", "error", "action"]
    component: str = Field(max_length=100)
    message: str = Field(max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None


@router.post('/frontend', status_code=202, tags=["internal-logs"])
async def ingest_frontend_logs(payload: list[FrontendLogIn]):
    if len(payload) > 50:
        raise HTTPException(400, "Batch too large. Max 50.")
    for entry in payload:
        try:
            log_func = getattr(
                logger,
                entry.level if entry.level != "action" else "info",
                logger.info
            )
            safe_meta = {
                k: v for k, v in entry.metadata.items()
                if k not in ("source", "component", "user_id", "timestamp", "message")
            }
            log_func(
                entry.message,
                source="frontend",
                component=entry.component,
                user_id=entry.user_id,
                timestamp=entry.timestamp.isoformat(),
                **safe_meta,
            )
        except Exception as exc:
            logger.warning("Failed to write frontend log entry", error=str(exc))
    return {"status": "accepted", "count": len(payload)}


@router.get('')
async def get_logs(
    tail: int = Query(100, description='Number of recent logs to fetch'),
    search: Optional[str] = Query(None, description='Filter log text'),
    source: Optional[str] = Query(None, description='Filter by source field')
):
    if not os.path.exists(LOG_FILE_PATH):
        return success_response(data=[])
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error('Failed to read logs', error=str(e))
        return success_response(data=[])

    parsed_logs = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        if search and search.lower() not in line.lower():
            continue
        try:
            parsed = json.loads(line)
            if source and parsed.get('source') != source:
                continue
            parsed_logs.append(parsed)
        except json.JSONDecodeError:
            parsed_logs.append({'message': line, 'level': 'unknown'})
        if len(parsed_logs) >= tail:
            break

    return success_response(data=parsed_logs, message='Logs retrieved successfully')