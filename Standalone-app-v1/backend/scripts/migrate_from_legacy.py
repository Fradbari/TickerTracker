import argparse
import asyncio
import csv
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field, field_validator, ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

# Add backend directory to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.shared.infra.database import AsyncSessionLocal
from src.estimates.domain.models import Estimate, Direction, EstimateStatus
from src.market_data.domain.models import MarketData
from src.shared.domain.models import Ticker

# Adjust root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- PYDANTIC VALIDATION MODELS (Task 5.17 Microstep 7) ---

class LegacyEstimateImport(BaseModel):
    ticker: str = Field(..., min_length=1)
    start_price: Decimal = Field(..., gt=0)
    target_price: Decimal = Field(..., gt=0)
    stop_loss_price: Decimal = Field(..., gt=0)
    target_profit_percent: Decimal
    stop_loss_percent: Decimal
    status: str
    direction: str
    created_at: datetime
    closed_at: datetime | None = None
    exit_price: Decimal | None = None
    realized_pnl: Decimal | None = None

    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = [e.value for e in EstimateStatus]
        # Legacy might have different status strings, mapping here:
        status_map = {
            "open": "OPEN", "closed": "CLOSED_MANUAL", "win": "CLOSED_WIN", "loss": "CLOSED_LOSS",
            "OPEN": "OPEN", "CLOSED_MANUAL": "CLOSED_MANUAL", "CLOSED_WIN": "CLOSED_WIN", "CLOSED_LOSS": "CLOSED_LOSS"
        }
        mapped = status_map.get(v.upper(), "CLOSED_MANUAL")
        if mapped not in valid_statuses:
            raise ValueError(f"Invalid status: {v}")
        return mapped

    @field_validator('direction')
    def validate_direction(cls, v):
        valid_dirs = [e.value for e in Direction]
        mapped = v.upper()
        if mapped not in valid_dirs:
            raise ValueError(f"Invalid direction: {v}")
        return mapped


class LegacyHistoryImport(BaseModel):
    ticker: str = Field(..., min_length=1)
    date: date
    open: Decimal = Field(..., gt=0)
    high: Decimal = Field(..., gt=0)
    low: Decimal = Field(..., gt=0)
    close: Decimal = Field(..., gt=0)
    volume: int = Field(..., ge=0)


# --- DRIVE CONNECTION (Microstep 2) ---
def connect_to_drive():
    """Connect to Google Drive using GOOGLE_SERVICE_ACCOUNT_CREDENTIALS."""
    creds_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS")
    if not creds_str:
        logger.error("GOOGLE_SERVICE_ACCOUNT_CREDENTIALS environment variable is not set")
        sys.exit(1)
        
    try:
        credentials_info = json.loads(creds_str)
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive API.")
        return service
    except Exception as e:
        logger.error(f"Failed to authenticate with Google Drive: {e}")
        sys.exit(1)


# --- DOWNLOAD DATA (Microstep 3) ---
def download_legacy_data(service, folder_id: str):
    """Download legacy JSON/CSV files from the specified Google Drive folder."""
    logger.info(f"Searching for legacy files in folder {folder_id}...")
    files_to_download = []
    
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        items = results.get('files', [])
        
        legacy_data = {"estimates": [], "history": []}
        
        for item in items:
            file_id = item['id']
            file_name = item['name']
            mime_type = item['mimeType']
            
            logger.info(f"Downloading {file_name}...")
            request = service.files().get_media(fileId=file_id)
            content = request.execute()
            
            if file_name.endswith('.json'):
                legacy_data["estimates"].extend(parse_legacy_json(content.decode('utf-8')))
            elif file_name.endswith('.csv'):
                legacy_data["history"].extend(parse_legacy_history(content.decode('utf-8')))
                
        return legacy_data
    except HttpError as error:
        logger.error(f"An error occurred reading Drive: {error}")
        sys.exit(1)


# --- PARSING FUNCTIONS (Microstep 4 & 5) ---
def parse_legacy_json(content: str) -> List[Dict[str, Any]]:
    """Parse legacy JSON containing estimates."""
    try:
        data = json.loads(content)
        # Handle variations in JSON structure (e.g. nested 'data' key or direct list)
        if isinstance(data, dict):
            return data.get("estimates", data.get("data", []))
        elif isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON content: {e}")
        return []

def parse_legacy_history(content: str) -> List[Dict[str, Any]]:
    """Parse legacy CSV containing market data history."""
    try:
        reader = csv.DictReader(content.splitlines())
        return [row for row in reader]
    except Exception as e:
        logger.error(f"Failed to parse CSV content: {e}")
        return []


# --- TRANSFORMATION (Microstep 6) ---
def transform_to_new_schema(legacy_data: Dict[str, List[Dict[str, Any]]]):
    """Transform legacy flat structures into expected DB shapes."""
    transformed_estimates = []
    transformed_history = []
    
    # Transform Estimates
    for item in legacy_data.get("estimates", []):
        try:
            # Map legacy names to new names
            transformed = {
                "ticker": item.get("ticker", item.get("symbol", "")).upper(),
                "start_price": Decimal(str(item.get("start_price", item.get("entry_price", 0)))),
                "target_price": Decimal(str(item.get("target_price", 0))),
                "stop_loss_price": Decimal(str(item.get("stop_loss_price", 0))),
                "target_profit_percent": Decimal(str(item.get("target_profit_percent", 0))),
                "stop_loss_percent": Decimal(str(item.get("stop_loss_percent", 0))),
                "status": item.get("status", "OPEN"),
                "direction": item.get("direction", "LONG"),
                "created_at": item.get("created_at", item.get("date", datetime.utcnow().isoformat())),
                "closed_at": item.get("closed_at"),
                "exit_price": item.get("exit_price") if item.get("exit_price") else None,
                "realized_pnl": item.get("realized_pnl") if item.get("realized_pnl") else None
            }
            # Remove falsy optional fields
            if not transformed["closed_at"]:
                transformed["closed_at"] = None
                
            transformed_estimates.append(transformed)
        except Exception as e:
            logger.warning(f"Error transforming estimate {item}: {e}")

    # Transform History
    for item in legacy_data.get("history", []):
        try:
            date_str = item.get("date", item.get("Date", ""))
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            
            transformed = {
                "ticker": item.get("ticker", item.get("Ticker", item.get("Symbol", ""))).upper(),
                "date": date_str,
                "open": Decimal(str(item.get("open", item.get("Open", 0)))),
                "high": Decimal(str(item.get("high", item.get("High", 0)))),
                "low": Decimal(str(item.get("low", item.get("Low", 0)))),
                "close": Decimal(str(item.get("close", item.get("Close", 0)))),
                "volume": int(float(item.get("volume", item.get("Volume", 0))))
            }
            transformed_history.append(transformed)
        except Exception as e:
            logger.warning(f"Error transforming history {item}: {e}")

    return {"estimates": transformed_estimates, "history": transformed_history}


# --- VALIDATION (Microstep 7) ---
def validate_transformed_data(data: Dict[str, List[Dict[str, Any]]]):
    """Validate data using Pydantic Models. Drops invalid records."""
    valid_estimates = []
    valid_history = []
    errors = {"estimates": 0, "history": 0}
    
    for item in data["estimates"]:
        try:
            valid_item = LegacyEstimateImport(**item)
            valid_estimates.append(valid_item)
        except ValidationError as e:
            errors["estimates"] += 1
            logger.debug(f"Estimate validation error: {e}")
            
    for item in data["history"]:
        try:
            valid_item = LegacyHistoryImport(**item)
            valid_history.append(valid_item)
        except ValidationError as e:
            errors["history"] += 1
            logger.debug(f"History validation error: {e}")
            
    return {"estimates": valid_estimates, "history": valid_history}, errors


# --- IMPORT / DATABASE (Microstep 8) ---
async def import_to_database(valid_data, dry_run: bool):
    """Import valid records to PostgreSQL using idempotent inserts."""
    session_factory = AsyncSessionLocal
    
    stats = {"estimates_inserted": 0, "history_inserted": 0, "tickers_created": 0}
    
    async with session_factory() as session:
        # 1. Resolve and create Tickers
        all_tickers = set(e.ticker for e in valid_data["estimates"]) | set(h.ticker for h in valid_data["history"])
        
        # Load existing tickers to get their IDs
        result = await session.execute(select(Ticker).where(Ticker.symbol.in_(all_tickers)))
        existing_tickers = {t.symbol: t.id for t in result.scalars().all()}
        
        for symbol in all_tickers:
            if symbol not in existing_tickers:
                if not dry_run:
                    new_ticker = Ticker(
                        symbol=symbol,
                        name=f"Imported {symbol}",
                        asset_type="stock",
                        currency="USD"
                    )
                    session.add(new_ticker)
                    await session.flush()
                    existing_tickers[symbol] = new_ticker.id
                    stats["tickers_created"] += 1
                else:
                    logger.info(f"[DRY-RUN] Would create ticker {symbol}")
                    existing_tickers[symbol] = uuid.uuid4() # Mock ID
                    
        if not dry_run:
            await session.commit()

        # 2. Insert market_data (History) idempotently
        if valid_data["history"]:
            history_rows = []
            for h in valid_data["history"]:
                history_rows.append({
                    "ticker_id": existing_tickers[h.ticker],
                    "date": h.date,
                    "open": h.open,
                    "high": h.high,
                    "low": h.low,
                    "close": h.close,
                    "volume": h.volume,
                    "data_source": "legacy_import"
                })
            
            if not dry_run:
                # Use insert().on_conflict_do_nothing()
                stmt = insert(MarketData).values(history_rows)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['ticker_id', 'date']
                )
                res = await session.execute(stmt)
                stats["history_inserted"] += res.rowcount
                await session.commit()
            else:
                logger.info(f"[DRY-RUN] Would insert chunk of {len(history_rows)} historical prices")
                stats["history_inserted"] += len(history_rows)
                
        # 3. Insert estimates idempotently
        if valid_data["estimates"]:
            estimate_rows = []
            for e in valid_data["estimates"]:
                # Generate a stable UUID5 to allow idempotency without DB unique constraints
                stable_id = uuid.uuid5(uuid.NAMESPACE_OID, f"legacy_{e.ticker}_{e.created_at.isoformat()}")
                
                estimate_rows.append({
                    "id": stable_id,
                    "ticker_id": existing_tickers[e.ticker],
                    "start_price": e.start_price,
                    "target_price": e.target_price,
                    "stop_loss_price": e.stop_loss_price,
                    "target_profit_percent": e.target_profit_percent,
                    "stop_loss_percent": e.stop_loss_percent,
                    "status": EstimateStatus(e.status),
                    "direction": Direction(e.direction),
                    "created_at": e.created_at,
                    "closed_at": e.closed_at,
                    "exit_price": e.exit_price,
                    "realized_pnl": e.realized_pnl
                })
            
            if not dry_run:
                stmt = insert(Estimate).values(estimate_rows)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=['id']  # Unique constraint on PK
                )
                res = await session.execute(stmt)
                stats["estimates_inserted"] += res.rowcount
                await session.commit()
            else:
                logger.info(f"[DRY-RUN] Would insert chunk of {len(estimate_rows)} estimates")
                stats["estimates_inserted"] += len(estimate_rows)

    return stats


# --- VERIFICATION (Microstep 9) ---
async def verify_migration(stats, valid_data):
    """Run counts check after migration to verify all rows are in DB."""
    logger.info("Verifying migration totals...")
    from sqlalchemy import func as sqla_func
    session_factory = AsyncSessionLocal
    
    async with session_factory() as session:
        # This isn't an exact 1-to-1 match since DB might have other data + skipped duplicates
        # But we print the DB count for safety
        db_est_count = await session.scalar(select(sqla_func.count()).select_from(Estimate))
        db_hist_count = await session.scalar(select(sqla_func.count()).select_from(MarketData))
        
        logger.info(f"Verification: DB now has {db_est_count} estimates and {db_hist_count} market data rows.")
        
        expected_est = len(valid_data["estimates"])
        if stats["estimates_inserted"] < expected_est:
            logger.warning(f"Inserted estimates ({stats['estimates_inserted']}) is less than parsed ({expected_est}). This could be due to duplicates being skipped.")


# --- MAIN EXECUTION ---
async def main():
    parser = argparse.ArgumentParser(description='Migrate legacy JSON/CSV from Google Drive to v3.0 Database.')
    parser.add_argument('--dry-run', action='store_true', help='Validate and simulate insert without committing')
    parser.add_argument('--source-folder-id', type=str, required=True, help='Google Drive Folder ID containing legacy data')
    parser.add_argument('--env-file', type=str, help='Path to .env file', default='.env')
    
    args = parser.parse_args()
    
    # Load dotenv
    import dotenv
    if os.path.exists(args.env_file):
        dotenv.load_dotenv(args.env_file)
        
    start_time = time.time()
    
    # Steps
    service = connect_to_drive()
    raw_data = download_legacy_data(service, args.source_folder_id)
    
    logger.info(f"Downloaded {len(raw_data['estimates'])} raw estimates and {len(raw_data['history'])} raw history rows.")
    
    transformed_data = transform_to_new_schema(raw_data)
    valid_data, errors = validate_transformed_data(transformed_data)
    
    logger.info(f"Passed Validation: {len(valid_data['estimates'])} estimates, {len(valid_data['history'])} history rows.")
    logger.info(f"Failed Validation: {errors['estimates']} estimates, {errors['history']} history rows.")

    stats = await import_to_database(valid_data, args.dry_run)
    
    if not args.dry_run:
        from sqlalchemy import func as sqla_func
        # Verify explicitly imports the specific sql funcs
        await verify_migration(stats, valid_data)
        
    # Build and save report
    duration = round(time.time() - start_time, 2)
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run": args.dry_run,
        "duration_seconds": duration,
        "source_folder_id": args.source_folder_id,
        "total_raw": {
            "estimates": len(raw_data["estimates"]),
            "history": len(raw_data["history"])
        },
        "errors": errors,
        "inserted": stats
    }
    
    report_file = f"migration_report_{int(start_time)}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Migration completed in {duration}s. Report saved to {report_file}")
    if errors["estimates"] > 0 or errors["history"] > 0:
        logger.warning(f"There were validation errors. Check the report for skipped rows.")


if __name__ == '__main__':
    asyncio.run(main())
