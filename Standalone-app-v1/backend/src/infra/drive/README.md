# Google Drive Integration

Async Google Drive API client for TickerTracker with service account authentication.

## Overview

The `GoogleDriveClient` provides a type-safe, async interface to Google Drive API operations, designed specifically for TickerTracker's synchronization needs.

## Features

- **Async Operations**: All methods use `asyncio` for non-blocking I/O
- **Service Account Auth**: Authenticate using Google Service Account credentials
- **Type Safety**: Strongly typed with dataclasses and type hints
- **Error Handling**: Comprehensive exception hierarchy for Drive errors
- **Logging**: Structured logging for all operations
- **Timeout Control**: Configurable timeout for API calls

## Quick Start

### 1. Configuration

Add your service account credentials to `.env`:

```env
GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "..."}' 
DRIVE_FOLDER_ID="1ABC...XYZ"
```

### 2. Initialize Client

```python
from src.infra.drive import GoogleDriveClient
from src.shared.infra.config import get_settings

settings = get_settings()

client = GoogleDriveClient(
    service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value(),
    timeout=30  # seconds
)
```

### 3. Basic Operations

```python
# List files in folder
files = await client.list_files(folder_id="1ABC...")
for file in files:
    print(f"{file.name} ({file.size} bytes)")

# Download file
content = await client.download_file(file_id="1XYZ...")
data = content.decode('utf-8')  # For text files

# Upload new file
new_file = await client.upload_file(
    folder_id="1ABC...",
    filename="portfolio.csv",
    content=b"ticker,shares\nAAPL,100",
    mime_type="text/csv"
)
print(f"Uploaded: {new_file.id}")

# Update existing file
updated = await client.update_file(
    file_id="1XYZ...",
    content=b"ticker,shares\nAAPL,150"
)
print(f"Updated: {updated.modified_time}")

# Delete file
success = await client.delete_file(file_id="1XYZ...")
```

## API Reference

### GoogleDriveClient

#### `__init__(service_account_json: str, timeout: int = 30)`

Initialize client with service account credentials.

**Parameters:**
- `service_account_json`: JSON string with service account credentials
- `timeout`: API operation timeout in seconds (default: 30)

**Raises:**
- `DriveAuthenticationError`: If authentication fails

---

#### `async list_files(folder_id: str, query: str = None, page_size: int = 100) -> List[DriveFile]`

List files in a Google Drive folder.

**Parameters:**
- `folder_id`: Google Drive folder ID
- `query`: Optional query string (Drive API query syntax)
- `page_size`: Number of files per page (max 1000, default 100)

**Returns:**
- List of `DriveFile` objects

**Raises:**
- `DriveFolderNotFoundError`: If folder doesn't exist
- `DrivePermissionError`: If no permission to access

**Examples:**
```python
# List all files
files = await client.list_files("1ABC...")

# List only CSV files
csv_files = await client.list_files(
    "1ABC...",
    query="mimeType='text/csv'"
)

# List files with "backup" in name
backups = await client.list_files(
    "1ABC...",
    query="name contains 'backup'"
)
```

---

#### `async download_file(file_id: str) -> bytes`

Download file content from Google Drive.

**Parameters:**
- `file_id`: Google Drive file ID

**Returns:**
- File content as bytes

**Raises:**
- `DriveFileNotFoundError`: If file doesn't exist
- `DriveDownloadError`: If download fails

**Example:**
```python
content = await client.download_file("1XYZ...")

# For text files
text = content.decode('utf-8')

# For CSV files
import csv
import io
reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
```

---

#### `async upload_file(folder_id: str, filename: str, content: bytes, mime_type: str = 'application/octet-stream') -> DriveFile`

Upload a new file to Google Drive.

**Parameters:**
- `folder_id`: Parent folder ID
- `filename`: Name for the new file
- `content`: File content as bytes
- `mime_type`: MIME type (default: 'application/octet-stream')

**Returns:**
- `DriveFile` representing the uploaded file

**Raises:**
- `DriveUploadError`: If upload fails
- `DriveFolderNotFoundError`: If parent folder doesn't exist
- `DriveQuotaExceededError`: If storage quota exceeded

**Example:**
```python
# Upload CSV file
file = await client.upload_file(
    folder_id="1ABC...",
    filename="portfolio.csv",
    content=b"ticker,shares\nAAPL,100",
    mime_type="text/csv"
)

# Upload JSON file
import json
data = {"ticker": "AAPL", "shares": 100}
file = await client.upload_file(
    folder_id="1ABC...",
    filename="data.json",
    content=json.dumps(data).encode('utf-8'),
    mime_type="application/json"
)
```

---

#### `async update_file(file_id: str, content: bytes, mime_type: str = None) -> DriveFile`

Update existing file content.

**Parameters:**
- `file_id`: ID of file to update
- `content`: New file content as bytes
- `mime_type`: Optional new MIME type (keeps original if None)

**Returns:**
- `DriveFile` representing the updated file

**Raises:**
- `DriveFileNotFoundError`: If file doesn't exist
- `DriveUploadError`: If update fails

**Example:**
```python
updated = await client.update_file(
    file_id="1XYZ...",
    content=b"ticker,shares\nAAPL,150"
)
print(f"Last modified: {updated.modified_time}")
```

---

#### `async delete_file(file_id: str) -> bool`

Delete a file from Google Drive.

**Parameters:**
- `file_id`: ID of file to delete

**Returns:**
- `True` if deletion successful

**Raises:**
- `DriveFileNotFoundError`: If file doesn't exist
- `DrivePermissionError`: If no permission to delete

**Example:**
```python
success = await client.delete_file("1XYZ...")
if success:
    print("File deleted successfully")
```

---

#### `async create_temp_file(folder_id: str, filename: str, mime_type: str = 'text/plain') -> DriveFile`

Create a temporary placeholder file.

Useful for lock files or placeholders that will be updated later.

**Parameters:**
- `folder_id`: Parent folder ID
- `filename`: Name for the temp file
- `mime_type`: MIME type (default: 'text/plain')

**Returns:**
- `DriveFile` representing the created temp file

**Raises:**
- `DriveUploadError`: If creation fails

**Example:**
```python
# Create lock file
lock = await client.create_temp_file(
    folder_id="1ABC...",
    filename=".sync_lock"
)

# Later update with content
await client.update_file(lock.id, b"locked by process X")
```

---

#### `async get_file_metadata(file_id: str) -> DriveFile`

Get metadata for a file without downloading content.

**Parameters:**
- `file_id`: Google Drive file ID

**Returns:**
- `DriveFile` with metadata

**Raises:**
- `DriveFileNotFoundError`: If file doesn't exist

**Example:**
```python
metadata = await client.get_file_metadata("1XYZ...")
print(f"Name: {metadata.name}")
print(f"Size: {metadata.size} bytes")
print(f"Modified: {metadata.modified_time}")
```

## Data Models

### DriveFile

Immutable dataclass representing a Google Drive file.

**Attributes:**
- `id: str` - Google Drive file ID
- `name: str` - File name
- `mime_type: str` - MIME type (e.g., 'text/csv')
- `size: Optional[int]` - File size in bytes (None for folders)
- `created_time: Optional[datetime]` - Creation timestamp
- `modified_time: Optional[datetime]` - Last modification timestamp
- `web_view_link: Optional[str]` - URL to view in Drive web UI
- `parent_folder_id: Optional[str]` - Parent folder ID

**Methods:**
- `is_folder() -> bool` - Check if this is a folder
- `is_csv() -> bool` - Check if this is a CSV file
- `is_json() -> bool` - Check if this is a JSON file

**Example:**
```python
file = await client.get_file_metadata("1XYZ...")

if file.is_csv():
    content = await client.download_file(file.id)
    # Process CSV...
```

### DriveFileMetadata

Metadata for creating or updating files (currently unused in main API).

## Exception Hierarchy

All exceptions inherit from `DriveError` base class:

```
DriveError (message, details)
├── DriveAuthenticationError
├── DriveFileNotFoundError (file_id)
├── DriveFolderNotFoundError (folder_id)
├── DriveUploadError (filename)
├── DriveDownloadError (file_id)
├── DriveQuotaExceededError
├── DrivePermissionError (operation)
└── DriveTimeoutError (operation, timeout)
```

### Error Handling Example

```python
from src.infra.drive.exceptions import (
    DriveFileNotFoundError,
    DrivePermissionError,
    DriveQuotaExceededError,
    DriveError,
)

try:
    content = await client.download_file("1XYZ...")
except DriveFileNotFoundError as e:
    print(f"File not found: {e.file_id}")
except DrivePermissionError as e:
    print(f"Permission denied: {e.operation}")
except DriveQuotaExceededError:
    print("Storage quota exceeded!")
except DriveError as e:
    print(f"Drive error: {e.message}")
    print(f"Details: {e.details}")
```

## Advanced Usage

### Filtering Files

Use Drive API query syntax for advanced filtering:

```python
# Files created after date
files = await client.list_files(
    "1ABC...",
    query="createdTime > '2024-01-01T00:00:00'"
)

# Files larger than 1MB
files = await client.list_files(
    "1ABC...",
    query="size > 1048576"
)

# Combine conditions with 'and'/'or'
files = await client.list_files(
    "1ABC...",
    query="mimeType='text/csv' and name contains 'portfolio'"
)
```

### Batch Operations

```python
# Upload multiple files
folder_id = "1ABC..."
files_to_upload = [
    ("portfolio.csv", b"...", "text/csv"),
    ("estimates.json", b"...", "application/json"),
]

uploaded = []
for filename, content, mime_type in files_to_upload:
    file = await client.upload_file(
        folder_id=folder_id,
        filename=filename,
        content=content,
        mime_type=mime_type
    )
    uploaded.append(file)

print(f"Uploaded {len(uploaded)} files")
```

### Progress Tracking

```python
import logging

# Enable debug logging to see download progress
logging.basicConfig(level=logging.DEBUG)

# Downloads will log progress: "Download 50% complete"
content = await client.download_file("large_file_id")
```

## Testing

The module includes comprehensive unit tests with mocked Google API:

```bash
# Run all Drive client tests
pytest tests/infra/test_drive_client.py -v

# Run specific test class
pytest tests/infra/test_drive_client.py::TestListFiles -v

# Run with coverage
pytest tests/infra/test_drive_client.py --cov=src.infra.drive
```

Current test coverage: 16/16 tests passing ✅

## Performance Considerations

1. **Connection Reuse**: The client creates a single Google Drive service instance that's reused for all operations
2. **Async I/O**: All blocking operations run in executor to avoid blocking the event loop
3. **Batch Listings**: Use `page_size` parameter to control memory usage for large folders
4. **Timeout Control**: Configure timeout based on your network conditions and file sizes

## Security Best Practices

1. **Service Account Permissions**: Grant only necessary permissions to the service account
2. **Credential Storage**: Store `GOOGLE_SERVICE_ACCOUNT_JSON` in environment variables or secure vaults
3. **Folder Access**: Use specific folder IDs instead of root folder access
4. **Error Logging**: Avoid logging credentials in error messages (already handled by the client)

## Troubleshooting

### Authentication Errors

```
DriveAuthenticationError: Failed to authenticate with Google Drive
```

**Solution**: Verify your service account JSON is valid and properly formatted.

### Permission Denied

```
DrivePermissionError: Permission denied for operation: list_files
```

**Solution**: Ensure the service account has access to the folder. Share the folder with the service account email.

### Quota Exceeded

```
DriveQuotaExceededError: Google Drive storage quota exceeded
```

**Solution**: Free up space in your Drive account or upgrade your storage plan.

### File Not Found

```
DriveFileNotFoundError: File not found in Google Drive: 1XYZ...
```

**Solution**: Verify the file ID is correct and the file hasn't been deleted.

## Related Documentation

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Service Account Authentication](https://developers.google.com/identity/protocols/oauth2/service-account)
- [Drive API Query Syntax](https://developers.google.com/drive/api/v3/search-files)

## Support

For issues or questions:
1. Check the exception details in `e.details`
2. Review application logs (structured logging enabled)
3. Consult the test suite for usage examples
