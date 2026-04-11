import asyncio
import contextlib
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
from cryptography.fernet import Fernet
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import json
from google.oauth2 import service_account

from src.shared.infra.config import settings

# Configure logging for the script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def send_alert(message: str) -> None:
    """Send alert via webhook if configured."""
    if not settings.ALERT_WEBHOOK_URL:
        logger.warning(f"Alert not sent (no webhook configured): {message}")
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(settings.ALERT_WEBHOOK_URL, json={"text": message})
            logger.info("Alert sent successfully")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def get_google_credentials():
    """Get authenticated Google credentials from settings."""
    service_account_json = settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value()
    if not service_account_json or service_account_json.strip() == "":
        raise ValueError("Google Service Account JSON is empty or not configured.")
    service_account_info = json.loads(service_account_json)
    return service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    )

def get_drive_service():
    """Get authenticated Google Drive service."""
    creds = get_google_credentials()
    return build('drive', 'v3', credentials=creds)


def manage_retention(service, folder_id: str, retain_count: int = 30) -> None:
    """Keep the `retain_count` most recent backups, delete the rest."""
    try:
        # Retrieve files in the backup folder, ordered by creation time descending
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            orderBy="createdTime desc",
            fields="files(id, name, createdTime)"
        ).execute()

        files = results.get("files", [])
        logger.info(f"Found {len(files)} backups in folder. Keeping {retain_count}.")

        # Delete older files
        for f in files[retain_count:]:
            service.files().delete(fileId=f['id']).execute()
            logger.info(f"Deleted old backup: {f['name']} ({f['id']})")
    except Exception as e:
        logger.error(f"Error managing backup retention: {e}")
        raise


async def create_full_backup() -> None:
    """
    Create a pg_dump custom compressed backup, encrypt it, and upload to Drive.
    """
    logger.info("Starting database backup process...")
    # Generate timestamp
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"ticker_tracker_db_{ts}.dump"
    enc_filename = f"{backup_filename}.enc"
    
    # We will use tempfile to avoid leaking dumps on the filesystem
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dump_path = Path(tmp_dir) / backup_filename
            enc_path = Path(tmp_dir) / enc_filename

            # 1. pg_dump
            logger.info(f"Running pg_dump to {dump_path}")
            # Note: DATABASE_URL should be a proper postgres connection string
            db_url = settings.DATABASE_URL.get_secret_value()
            if db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

            # Environment variable for password for pg_dump (optional but safer than inline)
            # Actually, pg_dump handles connection strings seamlessly
            result = subprocess.run([
                "pg_dump",
                f"--dbname={db_url}",
                "--format=custom",
                "--compress=9",
                f"--file={dump_path}"
            ], capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                raise RuntimeError(f"pg_dump failed (exit {result.returncode}):\n{result.stderr or result.stdout}")
                
            logger.info(f"Dump successful. Size: {dump_path.stat().st_size} bytes")

            # 2. Encrypt
            logger.info("Encrypting backup...")
            key = settings.BACKUP_ENCRYPTION_KEY.get_secret_value().encode('utf-8')
            fernet = Fernet(key)
            
            # Note limitation: Fernet loads the whole file into RAM. 
            # For >500MB backups, cryptography.hazmat with AES-GCM streaming should be used.
            with open(dump_path, 'rb') as unenc_file:
                encrypted_data = fernet.encrypt(unenc_file.read())
                
            with open(enc_path, 'wb') as enc_file:
                enc_file.write(encrypted_data)
                
            logger.info(f"Encryption successful. Encrypted size: {enc_path.stat().st_size} bytes")

            # 3. Upload to Google Drive
            logger.info("Uploading to Google Drive...")
            service = get_drive_service()
            folder_id = settings.BACKUP_DRIVE_FOLDER_ID

            file_metadata = {
                'name': enc_filename,
                'parents': [folder_id]
            }
            media = MediaFileUpload(str(enc_path), resumable=True)
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"Upload complete. File ID: {uploaded_file.get('id')}")

            # 4. Retention Policy
            manage_retention(service, folder_id, retain_count=30)
            
            logger.info("Backup process completed successfully.")

    except Exception as e:
        err_msg = f"Database backup failed: {str(e)}"
        logger.error(err_msg)
        await send_alert(err_msg)
        raise


async def verify_backup(backup_file_id: str) -> bool:
    """
    Download a backup by ID, decrypt, and run pg_restore --list to verify integrity.
    """
    logger.info(f"Starting backup verification for File ID: {backup_file_id}")
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            enc_path = Path(tmp_dir) / "downloaded.enc"
            dump_path = Path(tmp_dir) / "downloaded.dump"

            # 1. Download
            logger.info("Downloading backup...")
            service = get_drive_service()
            request = service.files().get_media(fileId=backup_file_id)
            
            with open(enc_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            # 2. Decrypt
            logger.info("Decrypting backup...")
            key = settings.BACKUP_ENCRYPTION_KEY.get_secret_value().encode('utf-8')
            fernet = Fernet(key)
            
            with open(enc_path, 'rb') as f:
                decrypted_data = fernet.decrypt(f.read())
                
            with open(dump_path, 'wb') as f:
                f.write(decrypted_data)

            # 3. Verify using pg_restore --list
            logger.info("Verifying backup with pg_restore...")
            result = subprocess.run([
                "pg_restore",
                "--list",
                "--format=custom",
                str(dump_path)
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info("Backup verification successful! Content listed correctly.")
                return True
            else:
                raise RuntimeError(f"pg_restore verification failed (exit {result.returncode}):\n{result.stderr or result.stdout}")
                
    except Exception as e:
        err_msg = f"Backup verification failed for file {backup_file_id}: {str(e)}"
        logger.error(err_msg)
        await send_alert(err_msg)
        return False

async def verify_latest_backup() -> None:
    """Verify the most recent backup uploaded to Drive."""
    try:
        service = get_drive_service()
        folder_id = settings.BACKUP_DRIVE_FOLDER_ID
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            orderBy="createdTime desc",
            pageSize=1,
            fields="files(id, name)"
        ).execute()

        files = results.get("files", [])
        if not files:
            logger.warning("No backups found to verify.")
            return

        latest_file = files[0]
        logger.info(f"Found latest backup: {latest_file['name']}")
        
        await verify_backup(latest_file['id'])
        
    except Exception as e:
        logger.error(f"Failed to verify latest backup: {e}")
        await send_alert(f"Failed to execute weekly verify_latest_backup: {e}")


if __name__ == "__main__":
    # If run standalone, run the full backup procedure
    asyncio.run(create_full_backup())
