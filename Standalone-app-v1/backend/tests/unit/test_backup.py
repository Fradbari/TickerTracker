import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.fernet import Fernet

from scripts.backup import create_full_backup, manage_retention, send_alert, verify_backup

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock application settings."""
    class MockSettings:
        def __init__(self):
            key = Fernet.generate_key().decode('utf-8')
            class MockSecretStr:
                def __init__(self, val):
                    self.val = val
                def get_secret_value(self):
                    return self.val

            self.BACKUP_ENCRYPTION_KEY = MockSecretStr(key)
            self.DATABASE_URL = MockSecretStr("postgresql://user:pass@localhost:5432/db")
            self.BACKUP_DRIVE_FOLDER_ID = "mock_folder_id"
            self.ALERT_WEBHOOK_URL = "http://mock.webhook/alert"

    settings = MockSettings()
    
    # We patch exactly where the script imports settings
    monkeypatch.setattr("scripts.backup.settings", settings)
    return settings


@pytest.fixture
def mock_drive_service():
    """Mock the Google Drive API service."""
    service = MagicMock()
    # Mocking files().create().execute()
    files_mock = MagicMock()
    service.files.return_value = files_mock
    
    # Create
    create_req = MagicMock()
    create_req.execute.return_value = {'id': 'uploaded_file_id'}
    files_mock.create.return_value = create_req
    
    # List
    list_req = MagicMock()
    list_req.execute.return_value = {
        'files': [{'id': f'file_{i}', 'name': f'backup_{i}.enc'} for i in range(35)]
    }
    files_mock.list.return_value = list_req
    
    # Delete
    del_req = MagicMock()
    del_req.execute.return_value = {}
    files_mock.delete.return_value = del_req

    return service


@pytest.mark.asyncio
async def test_alerting_called_on_exception(mock_settings, monkeypatch):
    """Test alerting webhook is fired when backup fails."""
    # Mock send_alert to see if it's called
    mock_post = AsyncMock()
    monkeypatch.setattr("scripts.backup.httpx.AsyncClient.post", mock_post)

    with patch("scripts.backup.subprocess.run") as mock_run:
        # Simulate pg_dump failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Database connection failed"

        with pytest.raises(Exception, match="pg_dump failed"):
            await create_full_backup()

        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert "json" in call_kwargs
        assert "pg_dump failed" in call_kwargs["json"]["text"]


def test_manage_retention(mock_drive_service):
    """Test retention policy keeps correct number of files and deletes the rest."""
    # We mocked 35 files in the drive. If we ask to retain 30, it should delete 5.
    manage_retention(mock_drive_service, "mock_folder_id", retain_count=30)
    
    assert mock_drive_service.files().delete.call_count == 5


@pytest.mark.asyncio
async def test_create_full_backup_success(mock_settings, mock_drive_service, monkeypatch, tmp_path):
    """Test the full complete round of a backup creation mock."""
    monkeypatch.setattr("scripts.backup.get_drive_service", lambda: mock_drive_service)
    
    with patch("scripts.backup.subprocess.run") as mock_run, \
         patch("scripts.backup.tempfile.TemporaryDirectory") as mock_temp_dir:
        
        # We need to simulate that pg_dump creates a file
        def fake_run(*args, **kwargs):
            # args[0] is the command list, look for '--file=...'
            file_arg = next(arg for arg in args[0] if arg.startswith("--file="))
            file_path = file_arg.split("=")[1]
            # Write dummy data so encryption doesn't fail
            with open(file_path, "w") as f:
                f.write("dummy db dump")
            mock_res = MagicMock()
            mock_res.returncode = 0
            return mock_res
            
        mock_run.side_effect = fake_run
        
        # Use pytest tmp_path to fake tempdir
        mock_temp_dir.return_value.__enter__.return_value = tmp_path
        
        # Run it
        await create_full_backup()
        
        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "pg_dump"
        assert cmd[1] == "--dbname=postgresql://user:pass@localhost:5432/db"
        assert "--format=custom" in cmd
        assert "--compress=9" in cmd
        
        # Check that it uploaded via Drive
        mock_drive_service.files().create.assert_called_once()


@pytest.mark.asyncio
async def test_verify_backup_success(mock_settings, monkeypatch, tmp_path):
    """Test the verification step round trip."""
    # Create an encrypted 'downloaded' file directly for the test
    key = mock_settings.BACKUP_ENCRYPTION_KEY.get_secret_value().encode('utf-8')
    fernet = Fernet(key)
    
    mock_enc_content = fernet.encrypt(b"dummy sql content")

    class FakeDownloader:
        def __init__(self, fh, *args):
            fh.write(mock_enc_content)
            self.done = True
        def next_chunk(self):
            return "status", self.done

    monkeypatch.setattr("scripts.backup.MediaIoBaseDownload", FakeDownloader)
    
    mock_drive_service = MagicMock()
    mock_drive_service.files().get_media.return_value = "mock_request"
    monkeypatch.setattr("scripts.backup.get_drive_service", lambda: mock_drive_service)
    
    with patch("scripts.backup.subprocess.run") as mock_run, \
         patch("scripts.backup.tempfile.TemporaryDirectory") as mock_temp_dir:
         
        mock_temp_dir.return_value.__enter__.return_value = tmp_path

        mock_run_res = MagicMock()
        mock_run_res.returncode = 0
        mock_run_res.stdout = "table1\ntable2"
        mock_run.return_value = mock_run_res

        result = await verify_backup("mock_file_id")
        
        assert result is True
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "pg_restore"
        assert cmd[1] == "--list"
