"""
Google Drive API client for TickerTracker.

Provides async interface to Google Drive API for file operations
with service account authentication.
"""

import asyncio
import io
import json
import logging
from datetime import datetime
from functools import wraps

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from src.infra.drive.exceptions import (
    DriveAuthenticationError,
    DriveDownloadError,
    DriveError,
    DriveFileNotFoundError,
    DriveFolderNotFoundError,
    DrivePermissionError,
    DriveQuotaExceededError,
    DriveTimeoutError,
    DriveUploadError,
)
from src.infra.drive.models import DriveFile

logger = logging.getLogger(__name__)


# Scopes required for Drive operations
DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]


def async_wrapper(func):
    """Decorator to run synchronous Google API calls in executor."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class GoogleDriveClient:
    """
    Async Google Drive API client with service account authentication.

    Provides methods for CRUD operations on Drive files with proper
    error handling, logging, and metrics.

    Example:
        ```python
        from src.infra.drive.client import GoogleDriveClient

        # Initialize with service account credentials
        client = GoogleDriveClient(
            service_account_json='{"type": "service_account", ...}',
            timeout=30
        )

        # List files in folder
        files = await client.list_files(folder_id='1ABC...')

        # Download file
        content = await client.download_file(file_id='1XYZ...')

        # Upload new file
        new_file = await client.upload_file(
            folder_id='1ABC...',
            filename='data.csv',
            content=b'ticker,price\\nAAPL,150.00',
            mime_type='text/csv'
        )
        ```
    """

    def __init__(
        self,
        service_account_json: str,
        timeout: int = 30,
    ):
        """
        Initialize Google Drive client.

        Args:
            service_account_json: JSON string containing service account credentials
            timeout: Timeout for API operations in seconds (default: 30)

        Raises:
            DriveAuthenticationError: If authentication fails
        """
        self._timeout = timeout
        self._service = None
        self._credentials = None

        try:
            # Parse service account JSON
            if not service_account_json or service_account_json.strip() == "":
                raise ValueError("Service account JSON is empty")

            service_account_info = json.loads(service_account_json)

            # Create credentials
            self._credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=DRIVE_SCOPES
            )

            # Build Drive service
            self._service = build('drive', 'v3', credentials=self._credentials)

            logger.info("Google Drive client initialized successfully")

        except json.JSONDecodeError as e:
            raise DriveAuthenticationError(f"Invalid service account JSON: {e}")
        except Exception as e:
            raise DriveAuthenticationError(f"Failed to initialize Drive client: {e}")

    def _parse_drive_file(self, file_metadata: dict) -> DriveFile:
        """
        Parse Google Drive API file metadata into DriveFile model.

        Args:
            file_metadata: Raw file metadata from Drive API

        Returns:
            DriveFile instance
        """
        return DriveFile(
            id=file_metadata['id'],
            name=file_metadata['name'],
            mime_type=file_metadata['mimeType'],
            size=int(file_metadata.get('size', 0)) if 'size' in file_metadata else None,
            created_time=datetime.fromisoformat(
                file_metadata['createdTime'].replace('Z', '+00:00')
            ) if 'createdTime' in file_metadata else None,
            modified_time=datetime.fromisoformat(
                file_metadata['modifiedTime'].replace('Z', '+00:00')
            ) if 'modifiedTime' in file_metadata else None,
            web_view_link=file_metadata.get('webViewLink'),
            parent_folder_id=file_metadata['parents'][0] if 'parents' in file_metadata else None,
        )

    def _handle_http_error(self, error: HttpError, operation: str) -> Exception:
        """
        Convert HttpError into typed exception.

        Args:
            error: HttpError from Google API
            operation: Operation that failed (for logging)

        Returns:
            Appropriate typed exception
        """
        status_code = error.resp.status
        reason = error.error_details if hasattr(error, 'error_details') else str(error)

        logger.error(f"Drive API error during {operation}: {status_code} - {reason}")

        if status_code == 404:
            return DriveFileNotFoundError("unknown", f"{operation}: {reason}")
        elif status_code == 403:
            if 'quota' in str(reason).lower():
                return DriveQuotaExceededError(f"{operation}: {reason}")
            return DrivePermissionError(operation, f"{reason}")
        elif status_code == 408 or status_code == 504:
            return DriveTimeoutError(operation, self._timeout, f"{reason}")
        else:
            return DriveError(f"Drive API error during {operation}", f"{status_code}: {reason}")

    async def list_files(
        self,
        folder_id: str,
        query: str | None = None,
        page_size: int = 100,
    ) -> list[DriveFile]:
        """
        List files in a Google Drive folder (fetches all pages).
        """
        try:
            logger.info(f"Listing files in folder: {folder_id}")
            base_query = f"'{folder_id}' in parents and trashed=false"
            if query:
                base_query = f"{base_query} and ({query})"

            all_files = []
            page_token = None
            loop = asyncio.get_event_loop()
            while True:
                def _list():
                    req = self._service.files().list(
                        q=base_query,
                        pageSize=page_size,
                        fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents)",
                        orderBy="modifiedTime desc",
                        pageToken=page_token
                    )
                    return req.execute()

                results = await loop.run_in_executor(None, _list)
                files = [self._parse_drive_file(f) for f in results.get('files', [])]
                all_files.extend(files)
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            logger.info(f"Found {len(all_files)} files in folder {folder_id}")
            return all_files

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFolderNotFoundError(folder_id, str(e))
            raise self._handle_http_error(e, "list_files")
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            raise DriveError(f"Failed to list files in folder {folder_id}", str(e))

    async def download_file(self, file_id: str) -> bytes:
        """
        Download file content from Google Drive.

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as bytes

        Raises:
            DriveFileNotFoundError: If file doesn't exist
            DriveDownloadError: If download fails
            DrivePermissionError: If no permission to download

        Example:
            >>> content = await client.download_file('1XYZ...')
            >>> data = content.decode('utf-8')  # For text files
        """
        try:
            logger.info(f"Downloading file: {file_id}")

            # Get file metadata first to verify it exists
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._service.files().get(
                    fileId=file_id,
                    fields="id, name, mimeType"
                ).execute()
            )

            # Download file content
            request = self._service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = await loop.run_in_executor(None, downloader.next_chunk)
                if status:
                    logger.debug(f"Download {int(status.progress() * 100)}% complete")

            content = fh.getvalue()
            logger.info(f"Downloaded file {file_id}: {len(content)} bytes")

            return content

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFileNotFoundError(file_id, str(e))
            raise self._handle_http_error(e, "download_file")
        except Exception as e:
            logger.error(f"Unexpected error downloading file {file_id}: {e}")
            raise DriveDownloadError(file_id, str(e))

    async def upload_file(
        self,
        folder_id: str,
        filename: str,
        content: bytes,
        mime_type: str = 'application/octet-stream',
    ) -> DriveFile:
        """
        Upload a new file to Google Drive.

        Args:
            folder_id: Parent folder ID
            filename: Name for the new file
            content: File content as bytes
            mime_type: MIME type (default: 'application/octet-stream')

        Returns:
            DriveFile representing the uploaded file

        Raises:
            DriveUploadError: If upload fails
            DriveFolderNotFoundError: If parent folder doesn't exist
            DriveQuotaExceededError: If storage quota exceeded

        Example:
            >>> file = await client.upload_file(
            ...     folder_id='1ABC...',
            ...     filename='portfolio.csv',
            ...     content=b'ticker,shares\\nAAPL,100',
            ...     mime_type='text/csv'
            ... )
            >>> print(f"Uploaded: {file.id}")
        """
        try:
            logger.info(f"Uploading file '{filename}' to folder {folder_id}")

            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': mime_type,
            }

            # Create media upload
            fh = io.BytesIO(content)
            media = MediaIoBaseUpload(
                fh,
                mimetype=mime_type,
                resumable=True
            )

            # Execute upload
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents"
                ).execute()
            )

            drive_file = self._parse_drive_file(result)
            logger.info(f"Uploaded file '{filename}' with ID: {drive_file.id}")

            return drive_file

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFolderNotFoundError(folder_id, str(e))
            raise self._handle_http_error(e, "upload_file")
        except Exception as e:
            logger.error(f"Unexpected error uploading file '{filename}': {e}")
            raise DriveUploadError(filename, str(e))

    async def update_file(
        self,
        file_id: str,
        content: bytes,
        mime_type: str | None = None,
    ) -> DriveFile:
        """
        Update existing file content in Google Drive.

        Args:
            file_id: ID of file to update
            content: New file content as bytes
            mime_type: Optional new MIME type (keeps original if None)

        Returns:
            DriveFile representing the updated file

        Raises:
            DriveFileNotFoundError: If file doesn't exist
            DriveUploadError: If update fails
            DrivePermissionError: If no permission to update

        Example:
            >>> updated = await client.update_file(
            ...     file_id='1XYZ...',
            ...     content=b'ticker,shares\\nAAPL,150'
            ... )
            >>> print(f"Updated: {updated.modified_time}")
        """
        try:
            logger.info(f"Updating file: {file_id}")

            # Prepare update metadata (only if mime_type is provided)
            file_metadata = {}
            if mime_type:
                file_metadata['mimeType'] = mime_type

            # Create media upload
            fh = io.BytesIO(content)
            media = MediaIoBaseUpload(
                fh,
                mimetype=mime_type or 'application/octet-stream',
                resumable=True
            )

            # Execute update
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.files().update(
                    fileId=file_id,
                    body=file_metadata if file_metadata else None,
                    media_body=media,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents"
                ).execute()
            )

            drive_file = self._parse_drive_file(result)
            logger.info(f"Updated file {file_id}: {drive_file.name}")

            return drive_file

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFileNotFoundError(file_id, str(e))
            raise self._handle_http_error(e, "update_file")
        except Exception as e:
            logger.error(f"Unexpected error updating file {file_id}: {e}")
            raise DriveUploadError(file_id, str(e))

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.

        Args:
            file_id: ID of file to delete

        Returns:
            True if deletion successful

        Raises:
            DriveFileNotFoundError: If file doesn't exist
            DrivePermissionError: If no permission to delete
            DriveError: For other API errors

        Example:
            >>> success = await client.delete_file('1XYZ...')
            >>> if success:
            ...     print("File deleted")
        """
        try:
            logger.info(f"Deleting file: {file_id}")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._service.files().delete(fileId=file_id).execute()
            )

            logger.info(f"Deleted file: {file_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFileNotFoundError(file_id, str(e))
            raise self._handle_http_error(e, "delete_file")
        except Exception as e:
            logger.error(f"Unexpected error deleting file {file_id}: {e}")
            raise DriveError(f"Failed to delete file {file_id}", str(e))

    async def create_temp_file(
        self,
        folder_id: str,
        filename: str,
        mime_type: str = 'text/plain',
    ) -> DriveFile:
        """
        Create a temporary placeholder file in Google Drive.

        Useful for creating lock files or placeholders that will be
        updated with actual content later.

        Args:
            folder_id: Parent folder ID
            filename: Name for the temp file
            mime_type: MIME type (default: 'text/plain')

        Returns:
            DriveFile representing the created temp file

        Raises:
            DriveUploadError: If creation fails
            DriveFolderNotFoundError: If parent folder doesn't exist

        Example:
            >>> temp = await client.create_temp_file(
            ...     folder_id='1ABC...',
            ...     filename='.lock'
            ... )
            >>> # Later update with actual content
            >>> await client.update_file(temp.id, b'locked by process X')
        """
        try:
            logger.info(f"Creating temp file '{filename}' in folder {folder_id}")

            # Create empty file with metadata only
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': mime_type,
            }

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.files().create(
                    body=file_metadata,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents"
                ).execute()
            )

            drive_file = self._parse_drive_file(result)
            logger.info(f"Created temp file '{filename}' with ID: {drive_file.id}")

            return drive_file

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFolderNotFoundError(folder_id, str(e))
            raise self._handle_http_error(e, "create_temp_file")
        except Exception as e:
            logger.error(f"Unexpected error creating temp file '{filename}': {e}")
            raise DriveUploadError(filename, str(e))

    async def get_file_metadata(self, file_id: str) -> DriveFile:
        """
        Get metadata for a specific file without downloading content.

        Args:
            file_id: Google Drive file ID

        Returns:
            DriveFile with metadata

        Raises:
            DriveFileNotFoundError: If file doesn't exist
            DrivePermissionError: If no permission to access
        """
        try:
            logger.debug(f"Getting metadata for file: {file_id}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._service.files().get(
                    fileId=file_id,
                    fields="id, name, mimeType, size, createdTime, modifiedTime, webViewLink, parents"
                ).execute()
            )

            return self._parse_drive_file(result)

        except HttpError as e:
            if e.resp.status == 404:
                raise DriveFileNotFoundError(file_id, str(e))
            raise self._handle_http_error(e, "get_file_metadata")
        except Exception as e:
            logger.error(f"Unexpected error getting file metadata {file_id}: {e}")
            raise DriveError(f"Failed to get file metadata {file_id}", str(e))
