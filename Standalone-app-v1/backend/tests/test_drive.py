# Manual test script (not auto-collected by pytest)
# Usage: py tests/test_drive.py
import asyncio

from src.infra.drive.client import GoogleDriveClient
from src.shared.infra.config import get_settings


async def _run_drive_check():
    settings = get_settings()

    client = GoogleDriveClient(
        service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value(),
        timeout=30
    )

    files = await client.list_files(settings.DRIVE_FOLDER_ID)
    print(f"Connessione riuscita! Trovati {len(files)} file nella cartella")

    for file in files:
        print(f"  - {file.name} ({file.mime_type})")

# Guard against pytest collection - only run when executed directly
if __name__ == "__main__":
    asyncio.run(_run_drive_check())
