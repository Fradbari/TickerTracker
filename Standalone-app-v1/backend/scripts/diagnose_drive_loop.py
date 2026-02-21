import os
import json
import traceback
import asyncio
import time

from src.infra.drive.client import GoogleDriveClient
from src.shared.infra.config import get_settings


def get_sa_and_folder():
    settings = get_settings()
    sa_json = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_JSON', None)
    folder_id = getattr(settings, 'DRIVE_FOLDER_ID', None)
    if not sa_json:
        sa_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not folder_id:
        folder_id = os.environ.get('DRIVE_FOLDER_ID')
    if hasattr(sa_json, 'get_secret_value'):
        try:
            sa_json = sa_json.get_secret_value()
        except Exception:
            pass
    return sa_json, folder_id


async def probe_once(client, folder_id, i):
    try:
        t0 = time.time()
        files = await client.list_files(folder_id=folder_id, page_size=1)
        dt = time.time()-t0
        print(f"[{i}] OK: listed {len(files)} files in {dt:.2f}s")
    except Exception as e:
        print(f"[{i}] ERROR: {type(e)} {e}")
        print(traceback.format_exc())


async def main():
    sa_json, folder_id = get_sa_and_folder()
    print('folder_id=', folder_id)
    if not sa_json:
        print('no sa json')
        return
    client = GoogleDriveClient(service_account_json=sa_json, timeout=30)
    for i in range(1,6):
        await probe_once(client, folder_id, i)
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
