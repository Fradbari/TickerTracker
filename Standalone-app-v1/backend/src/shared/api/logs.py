
import json
import os
import structlog
from typing import Any, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.shared.schemas.api_response import success_response

router = APIRouter(prefix='/api/logs', tags=['Logs'])
logger = structlog.get_logger(__name__)

LOG_FILE_PATH = '/app/logs/app.log'

class FrontendLogPayload(BaseModel):
    level: str
    message: str
    trace_id: Optional[str] = None
    meta: Optional[dict[str, Any]] = None

@router.post('/frontend')
async def receive_frontend_logs(payload: FrontendLogPayload):
    log_func = getattr(logger, payload.level.lower(), logger.info)
    meta = payload.meta or {}
    meta['source'] = 'frontend'
    if payload.trace_id:
        meta['trace_id'] = payload.trace_id

    log_func(payload.message, **meta)
    return success_response(data={'received': True}, message='Frontend log processed')

@router.get('')
async def get_logs(
    tail: int = Query(100, description='Number of recent logs to fetch'),
    search: Optional[str] = Query(None, description='Filter log text')
):
    if not os.path.exists(LOG_FILE_PATH):
        return success_response(data=[])

    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error('Failed to read logs', error=str(e))
        return success_response(data=[])

    # Filter and parse
    parsed_logs = []
    for line in reversed(lines):
        line = line.strip()
        if not line: continue
        if search and search.lower() not in line.lower():
            continue
        
        try:
            parsed = json.loads(line)
            parsed_logs.append(parsed)
        except json.JSONDecodeError:
            parsed_logs.append({'message': line, 'level': 'unknown'})
        
        if len(parsed_logs) >= tail:
            break
            
    return success_response(data=parsed_logs, message='Logs retrieved successfully')

