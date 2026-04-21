from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConfigBackup(BaseModel):
    finnhubKey: Optional[str] = None
    geminiKey: Optional[str] = None
    gasUrl: Optional[str] = None
    autoRefresh: Optional[bool] = None

class AppBackup(BaseModel):
    version: str = "4.0"
    timestamp: str
    estimates: List[Dict[str, Any]] = Field(default_factory=list)
    candles: List[Dict[str, Any]] = Field(default_factory=list)
    portfolio_snapshots: List[Dict[str, Any]] = Field(default_factory=list)
    config: ConfigBackup = Field(default_factory=ConfigBackup)
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    chatMessages: List[Dict[str, Any]] = Field(default_factory=list)

class SyncResult(BaseModel):
    success: bool
    file_id: Optional[str] = None
    file_name: str
    bytes_written: int
    duration_ms: int

class ImportResult(BaseModel):
    success: bool
    records_imported: int
    records_skipped: int
    warnings: List[str] = Field(default_factory=list)

class BackupFileInfo(BaseModel):
    file_id: str
    file_name: str
    timestamp_iso: str
    size_bytes: int

class SyncStatus(BaseModel):
    last_export_iso: Optional[str] = None
    last_import_iso: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None
    backups: List[BackupFileInfo] = Field(default_factory=list)
