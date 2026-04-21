import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.sync.services.gdrive_service import GDriveService
from src.sync.schemas.backup_schema import SyncResult

@pytest.mark.asyncio
async def test_export_to_gdrive_success():
    mock_db = AsyncMock()
    mock_db.execute.return_value = [] # Mock stime
    
    with patch('src.sync.services.gdrive_service.GoogleDriveClient') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_client_instance.upload_file.return_value = MagicMock(id='dummy_id')
        
        service = GDriveService(db=mock_db)
        service.client = mock_client_instance # Override con mock
        
        result = await service.export_to_gdrive()
        assert result.success == True
        assert result.file_id == 'dummy_id'

@pytest.mark.asyncio
async def test_import_from_gdrive_success():
    mock_db = AsyncMock()
    
    with patch('src.sync.services.gdrive_service.GoogleDriveClient') as MockClient:
        mock_client_instance = MockClient.return_value
        
        # Mock json backup file content
        import json
        dummy_content = json.dumps({"version": "4.0", "timestamp": "...", "estimates": [], "candles": [], "portfolio_snapshots": []}).encode("utf-8")
        mock_client_instance.download_file.return_value = dummy_content
        
        service = GDriveService(db=mock_db)
        service.client = mock_client_instance
        
        result = await service.import_from_gdrive(file_id='dummy_id')
        assert result.success == True
        assert result.records_imported >= 0
