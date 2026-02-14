"""
Unit tests for Google Drive client.

Tests the GoogleDriveClient with mocked Google API responses.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import json
import io

from src.infra.drive.client import GoogleDriveClient
from src.infra.drive.models import DriveFile
from src.infra.drive.exceptions import (
    DriveAuthenticationError,
    DriveFileNotFoundError,
    DriveFolderNotFoundError,
    DriveUploadError,
    DriveDownloadError,
    DrivePermissionError,
    DriveQuotaExceededError,
)
from googleapiclient.errors import HttpError


# Sample service account JSON for testing
MOCK_SERVICE_ACCOUNT_JSON = json.dumps({
    "type": "service_account",
    "project_id": "test-project",
    "private_key_id": "key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMOCK_KEY\\n-----END PRIVATE KEY-----\\n",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "client_id": "123456789",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
})


@pytest.fixture
def mock_drive_service():
    """Mock Google Drive service."""
    with patch('src.infra.drive.client.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service


@pytest.fixture
def mock_credentials():
    """Mock service account credentials."""
    with patch('src.infra.drive.client.service_account.Credentials.from_service_account_info') as mock_creds:
        mock_creds.return_value = Mock()
        yield mock_creds


@pytest.fixture
async def drive_client(mock_credentials, mock_drive_service):
    """Create GoogleDriveClient with mocked dependencies."""
    client = GoogleDriveClient(
        service_account_json=MOCK_SERVICE_ACCOUNT_JSON,
        timeout=30,
    )
    return client


class TestGoogleDriveClientInit:
    """Test client initialization."""
    
    def test_init_success(self, mock_credentials, mock_drive_service):
        """Test successful client initialization."""
        client = GoogleDriveClient(
            service_account_json=MOCK_SERVICE_ACCOUNT_JSON,
            timeout=30,
        )
        
        assert client._timeout == 30
        assert client._service is not None
        mock_credentials.assert_called_once()
    
    def test_init_invalid_json(self, mock_credentials):
        """Test initialization with invalid JSON."""
        with pytest.raises(DriveAuthenticationError) as exc_info:
            GoogleDriveClient(
                service_account_json="invalid json {",
                timeout=30,
            )
        assert "Invalid service account JSON" in exc_info.value.details
    
    def test_init_empty_json(self, mock_credentials):
        """Test initialization with empty JSON."""
        with pytest.raises(DriveAuthenticationError) as exc_info:
            GoogleDriveClient(
                service_account_json="",
                timeout=30,
            )
        assert "Service account JSON is empty" in exc_info.value.details


class TestListFiles:
    """Test list_files method."""
    
    @pytest.mark.asyncio
    async def test_list_files_success(self, drive_client, mock_drive_service):
        """Test successful file listing."""
        # Mock API response
        mock_files_list = Mock()
        mock_files_list.execute.return_value = {
            'files': [
                {
                    'id': 'file1',
                    'name': 'test.csv',
                    'mimeType': 'text/csv',
                    'size': '1024',
                    'createdTime': '2024-01-01T00:00:00.000Z',
                    'modifiedTime': '2024-01-01T00:00:00.000Z',
                    'webViewLink': 'https://drive.google.com/file/d/file1',
                    'parents': ['folder1']
                },
                {
                    'id': 'file2',
                    'name': 'data.json',
                    'mimeType': 'application/json',
                    'size': '2048',
                    'createdTime': '2024-01-02T00:00:00.000Z',
                    'modifiedTime': '2024-01-02T00:00:00.000Z',
                    'webViewLink': 'https://drive.google.com/file/d/file2',
                    'parents': ['folder1']
                }
            ]
        }
        
        mock_drive_service.files.return_value.list.return_value = mock_files_list
        
        # Execute
        files = await drive_client.list_files('folder1')
        
        # Assert
        assert len(files) == 2
        assert files[0].id == 'file1'
        assert files[0].name == 'test.csv'
        assert files[0].is_csv()
        assert files[1].id == 'file2'
        assert files[1].name == 'data.json'
        assert files[1].is_json()
    
    @pytest.mark.asyncio
    async def test_list_files_empty(self, drive_client, mock_drive_service):
        """Test listing empty folder."""
        mock_files_list = Mock()
        mock_files_list.execute.return_value = {'files': []}
        mock_drive_service.files.return_value.list.return_value = mock_files_list
        
        files = await drive_client.list_files('folder1')
        
        assert len(files) == 0
    
    @pytest.mark.asyncio
    async def test_list_files_not_found(self, drive_client, mock_drive_service):
        """Test listing non-existent folder."""
        mock_files_list = Mock()
        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'Not found'
        )
        mock_files_list.execute.side_effect = mock_error
        mock_drive_service.files.return_value.list.return_value = mock_files_list
        
        with pytest.raises(DriveFolderNotFoundError):
            await drive_client.list_files('nonexistent')


class TestDownloadFile:
    """Test download_file method."""
    
    @pytest.mark.asyncio
    async def test_download_success(self, drive_client, mock_drive_service):
        """Test successful file download."""
        # Mock file metadata
        mock_get = Mock()
        mock_get.execute.return_value = {
            'id': 'file1',
            'name': 'test.csv',
            'mimeType': 'text/csv'
        }
        
        # Mock file content download
        mock_get_media = Mock()
        mock_content = b'ticker,price\nAAPL,150.00'
        
        with patch('src.infra.drive.client.MediaIoBaseDownload') as mock_download:
            mock_downloader = Mock()
            mock_downloader.next_chunk.return_value = (Mock(progress=lambda: 1.0), True)
            mock_download.return_value = mock_downloader
            
            # Setup mocks
            mock_drive_service.files.return_value.get.return_value = mock_get
            mock_drive_service.files.return_value.get_media.return_value = mock_get_media
            
            # Mock BytesIO to return our content
            with patch('src.infra.drive.client.io.BytesIO') as mock_bytesio:
                mock_fh = Mock()
                mock_fh.getvalue.return_value = mock_content
                mock_bytesio.return_value = mock_fh
                
                # Execute
                content = await drive_client.download_file('file1')
                
                # Assert
                assert content == mock_content
    
    @pytest.mark.asyncio
    async def test_download_not_found(self, drive_client, mock_drive_service):
        """Test downloading non-existent file."""
        mock_get = Mock()
        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'Not found'
        )
        mock_get.execute.side_effect = mock_error
        mock_drive_service.files.return_value.get.return_value = mock_get
        
        with pytest.raises(DriveFileNotFoundError):
            await drive_client.download_file('nonexistent')


class TestUploadFile:
    """Test upload_file method."""
    
    @pytest.mark.asyncio
    async def test_upload_success(self, drive_client, mock_drive_service):
        """Test successful file upload."""
        mock_create = Mock()
        mock_create.execute.return_value = {
            'id': 'new_file',
            'name': 'upload.csv',
            'mimeType': 'text/csv',
            'size': '100',
            'createdTime': '2024-01-01T00:00:00.000Z',
            'modifiedTime': '2024-01-01T00:00:00.000Z',
            'webViewLink': 'https://drive.google.com/file/d/new_file',
            'parents': ['folder1']
        }
        
        mock_drive_service.files.return_value.create.return_value = mock_create
        
        # Execute
        result = await drive_client.upload_file(
            folder_id='folder1',
            filename='upload.csv',
            content=b'data',
            mime_type='text/csv'
        )
        
        # Assert
        assert result.id == 'new_file'
        assert result.name == 'upload.csv'
        assert result.mime_type == 'text/csv'
    
    @pytest.mark.asyncio
    async def test_upload_folder_not_found(self, drive_client, mock_drive_service):
        """Test upload to non-existent folder."""
        mock_create = Mock()
        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'Folder not found'
        )
        mock_create.execute.side_effect = mock_error
        mock_drive_service.files.return_value.create.return_value = mock_create
        
        with pytest.raises(DriveFolderNotFoundError):
            await drive_client.upload_file(
                folder_id='nonexistent',
                filename='test.csv',
                content=b'data',
                mime_type='text/csv'
            )
    
    @pytest.mark.asyncio
    async def test_upload_quota_exceeded(self, drive_client, mock_drive_service):
        """Test upload when quota exceeded."""
        mock_create = Mock()
        mock_error = HttpError(
            resp=Mock(status=403),
            content=b'Storage quota exceeded'
        )
        mock_error.error_details = 'Storage quota exceeded'
        mock_create.execute.side_effect = mock_error
        mock_drive_service.files.return_value.create.return_value = mock_create
        
        with pytest.raises(DriveQuotaExceededError):
            await drive_client.upload_file(
                folder_id='folder1',
                filename='test.csv',
                content=b'data',
                mime_type='text/csv'
            )


class TestUpdateFile:
    """Test update_file method."""
    
    @pytest.mark.asyncio
    async def test_update_success(self, drive_client, mock_drive_service):
        """Test successful file update."""
        mock_update = Mock()
        mock_update.execute.return_value = {
            'id': 'file1',
            'name': 'updated.csv',
            'mimeType': 'text/csv',
            'size': '200',
            'createdTime': '2024-01-01T00:00:00.000Z',
            'modifiedTime': '2024-01-02T00:00:00.000Z',
            'webViewLink': 'https://drive.google.com/file/d/file1',
            'parents': ['folder1']
        }
        
        mock_drive_service.files.return_value.update.return_value = mock_update
        
        # Execute
        result = await drive_client.update_file(
            file_id='file1',
            content=b'updated data'
        )
        
        # Assert
        assert result.id == 'file1'
        assert result.name == 'updated.csv'


class TestDeleteFile:
    """Test delete_file method."""
    
    @pytest.mark.asyncio
    async def test_delete_success(self, drive_client, mock_drive_service):
        """Test successful file deletion."""
        mock_delete = Mock()
        mock_delete.execute.return_value = None
        mock_drive_service.files.return_value.delete.return_value = mock_delete
        
        # Execute
        result = await drive_client.delete_file('file1')
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, drive_client, mock_drive_service):
        """Test deleting non-existent file."""
        mock_delete = Mock()
        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'Not found'
        )
        mock_delete.execute.side_effect = mock_error
        mock_drive_service.files.return_value.delete.return_value = mock_delete
        
        with pytest.raises(DriveFileNotFoundError):
            await drive_client.delete_file('nonexistent')


class TestCreateTempFile:
    """Test create_temp_file method."""
    
    @pytest.mark.asyncio
    async def test_create_temp_success(self, drive_client, mock_drive_service):
        """Test successful temp file creation."""
        mock_create = Mock()
        mock_create.execute.return_value = {
            'id': 'temp_file',
            'name': '.lock',
            'mimeType': 'text/plain',
            'createdTime': '2024-01-01T00:00:00.000Z',
            'modifiedTime': '2024-01-01T00:00:00.000Z',
            'parents': ['folder1']
        }
        
        mock_drive_service.files.return_value.create.return_value = mock_create
        
        # Execute
        result = await drive_client.create_temp_file(
            folder_id='folder1',
            filename='.lock'
        )
        
        # Assert
        assert result.id == 'temp_file'
        assert result.name == '.lock'


class TestGetFileMetadata:
    """Test get_file_metadata method."""
    
    @pytest.mark.asyncio
    async def test_get_metadata_success(self, drive_client, mock_drive_service):
        """Test successful metadata retrieval."""
        mock_get = Mock()
        mock_get.execute.return_value = {
            'id': 'file1',
            'name': 'test.csv',
            'mimeType': 'text/csv',
            'size': '1024',
            'createdTime': '2024-01-01T00:00:00.000Z',
            'modifiedTime': '2024-01-01T00:00:00.000Z',
            'webViewLink': 'https://drive.google.com/file/d/file1',
            'parents': ['folder1']
        }
        
        mock_drive_service.files.return_value.get.return_value = mock_get
        
        # Execute
        result = await drive_client.get_file_metadata('file1')
        
        # Assert
        assert result.id == 'file1'
        assert result.name == 'test.csv'
        assert result.size == 1024
