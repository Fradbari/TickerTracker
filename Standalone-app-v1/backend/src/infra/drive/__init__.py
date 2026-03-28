"""
Google Drive integration module.

Provides async client for Google Drive operations with service account authentication.
"""

from src.infra.drive.client import GoogleDriveClient
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
from src.infra.drive.models import DriveFile, DriveFileMetadata

__all__ = [
    # Client
    "GoogleDriveClient",
    # Models
    "DriveFile",
    "DriveFileMetadata",
    # Exceptions
    "DriveError",
    "DriveAuthenticationError",
    "DriveFileNotFoundError",
    "DriveFolderNotFoundError",
    "DriveUploadError",
    "DriveDownloadError",
    "DriveQuotaExceededError",
    "DrivePermissionError",
    "DriveTimeoutError",
]
