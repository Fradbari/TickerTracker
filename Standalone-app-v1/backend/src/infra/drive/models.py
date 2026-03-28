"""
Domain models for Google Drive integration.

Provides type-safe representations of Google Drive files and metadata.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DriveFile:
    """
    Represents a file in Google Drive.

    Immutable dataclass for type-safe handling of Drive file metadata.

    Attributes:
        id: Google Drive file ID
        name: File name
        mime_type: MIME type (e.g., 'text/csv', 'application/json')
        size: File size in bytes (None for folders)
        created_time: File creation timestamp
        modified_time: Last modification timestamp
        web_view_link: URL to view file in Drive web interface
        parent_folder_id: Parent folder ID (optional)
    """

    id: str
    name: str
    mime_type: str
    size: int | None = None
    created_time: datetime | None = None
    modified_time: datetime | None = None
    web_view_link: str | None = None
    parent_folder_id: str | None = None

    def is_folder(self) -> bool:
        """Check if this is a folder."""
        return self.mime_type == "application/vnd.google-apps.folder"

    def is_csv(self) -> bool:
        """Check if this is a CSV file."""
        return self.mime_type == "text/csv" or self.name.endswith(".csv")

    def is_json(self) -> bool:
        """Check if this is a JSON file."""
        return self.mime_type == "application/json" or self.name.endswith(".json")


@dataclass(frozen=True)
class DriveFileMetadata:
    """
    Metadata for creating or updating Drive files.

    Used when uploading or updating files to specify properties.

    Attributes:
        name: File name
        mime_type: MIME type
        parent_folder_id: Parent folder ID (for placement)
        description: File description (optional)
    """

    name: str
    mime_type: str
    parent_folder_id: str | None = None
    description: str | None = None
