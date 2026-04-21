from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# Assumiamo l'esistenza di un get_db in infra
# from src.infra.database import get_db
# Per il mockup usiamo una dependency fittizia se non esiste, ma normalmente:
async def get_db():
    yield None

from src.sync.services.gdrive_service import GDriveService
from src.sync.schemas.backup_schema import SyncResult, ImportResult, SyncStatus

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/export", response_model=SyncResult)
async def export_to_gdrive(db: AsyncSession = Depends(get_db)):
    service = GDriveService(db)
    result = await service.export_to_gdrive()
    if not result.success:
        raise HTTPException(status_code=500, detail="Export fallito")
    return result

@router.post("/import", response_model=ImportResult)
async def import_from_gdrive(file_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = GDriveService(db)
    result = await service.import_from_gdrive(file_id)
    if not result.success:
        raise HTTPException(status_code=500, detail="Import fallito")
    return result

@router.get("/status", response_model=SyncStatus)
async def get_sync_status(db: AsyncSession = Depends(get_db)):
    service = GDriveService(db)
    return await service.get_status()
