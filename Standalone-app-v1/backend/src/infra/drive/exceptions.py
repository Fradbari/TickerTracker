"""
Exceptions for Google Drive operations.

Provides typed exceptions for better error handling and debugging.
"""


class DriveError(Exception):
    """Base exception for all Google Drive errors."""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details


class DriveAuthenticationError(DriveError):
    """Raised when authentication with Google Drive fails."""

    def __init__(self, details: str = ""):
        super().__init__(
            "Failed to authenticate with Google Drive",
            details
        )


class DriveFileNotFoundError(DriveError):
    """Raised when a requested file is not found in Drive."""

    def __init__(self, file_id: str, details: str = ""):
        super().__init__(
            f"File not found in Google Drive: {file_id}",
            details
        )
        self.file_id = file_id


class DriveFolderNotFoundError(DriveError):
    """Raised when a requested folder is not found in Drive."""

    def __init__(self, folder_id: str, details: str = ""):
        super().__init__(
            f"Folder not found in Google Drive: {folder_id}",
            details
        )
        self.folder_id = folder_id


class DriveUploadError(DriveError):
    """Raised when file upload fails."""

    def __init__(self, filename: str, details: str = ""):
        super().__init__(
            f"Failed to upload file to Google Drive: {filename}",
            details
        )
        self.filename = filename


class DriveDownloadError(DriveError):
    """Raised when file download fails."""

    def __init__(self, file_id: str, details: str = ""):
        super().__init__(
            f"Failed to download file from Google Drive: {file_id}",
            details
        )
        self.file_id = file_id


class DriveQuotaExceededError(DriveError):
    """Raised when Drive storage quota is exceeded."""

    def __init__(self, details: str = ""):
        super().__init__(
            "Google Drive storage quota exceeded",
            details
        )


class DrivePermissionError(DriveError):
    """Raised when operation fails due to insufficient permissions."""

    def __init__(self, operation: str, details: str = ""):
        super().__init__(
            f"Permission denied for operation: {operation}",
            details
        )
        self.operation = operation


class DriveTimeoutError(DriveError):
    """Raised when operation times out."""

    def __init__(self, operation: str, timeout: int, details: str = ""):
        super().__init__(
            f"Operation timed out after {timeout}s: {operation}",
            details
        )
        self.operation = operation
        self.timeout = timeout
