import asyncio
import json
import os
import traceback

from src.infra.drive.client import GoogleDriveClient
from src.shared.infra.config import get_settings


def main():
    print("Starting Drive diagnostic...\n")
    try:
        settings = get_settings()
    except Exception as e:
        print("Failed to load settings:", e)
        settings = None

    sa_json = None
    folder_id = None

    if settings:
        sa_json = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_JSON', None)
        folder_id = getattr(settings, 'DRIVE_FOLDER_ID', None)

    # Fallback to env
    if not sa_json:
        sa_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not folder_id:
        folder_id = os.environ.get('DRIVE_FOLDER_ID')

    print(f"DRIVE_FOLDER_ID: {folder_id!r}\n")

    if not sa_json:
        print("No service account JSON configured (GOOGLE_SERVICE_ACCOUNT_JSON is empty). Exiting.")
        return

    # If the settings value is a Pydantic SecretStr, extract the raw string
    try:
        if hasattr(sa_json, "get_secret_value"):
            sa_json = sa_json.get_secret_value()
    except Exception:
        pass

    try:
        info = json.loads(sa_json)
        print("Service account keys loaded; client_email:", info.get('client_email'))
    except Exception as e:
        print("Failed to parse service account JSON:", e)
        print(traceback.format_exc())
        return

    # Attempt to instantiate client and list files
    try:
        client = GoogleDriveClient(service_account_json=sa_json, timeout=30)
    except Exception as e:
        print("Failed to initialize GoogleDriveClient:")
        print(type(e), e)
        print(traceback.format_exc())
        return

    async def run_check():
        try:
            print("Calling list_files(...) to probe folder access...")
            files = await client.list_files(folder_id=folder_id, page_size=1)
            print(f"OK: listed {len(files)} files (showing up to 1)")
            for f in files:
                print(f"- {f.id} {f.name}")
        except Exception as e:
            print("Exception during list_files call:")
            print(type(e), e)
            print(traceback.format_exc())

    asyncio.run(run_check())


if __name__ == '__main__':
    main()
