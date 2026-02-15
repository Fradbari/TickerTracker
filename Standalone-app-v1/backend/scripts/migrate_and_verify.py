import os
import asyncio
from tqdm import tqdm
from datetime import datetime
from src.shared.infra.config import get_settings
from src.infra.drive.client import GoogleDriveClient
from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.json_parser import LegacyJsonParser
from src.estimates.repositories.estimate_repository import EstimateRepository
from src.market_data.repositories.market_data_repository import MarketDataRepository
from src.market_data.domain.entities import Ticker
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()
DRIVE_FOLDER_ID = settings.DRIVE_FOLDER_ID

def format_file_info(file):
    return f"{file['name']} ({file['size']} bytes, modified: {file['modifiedTime']})"

async def verify_google_drive(drive_client):
    logger.info("Connecting to Google Drive...")
    try:
        files = await drive_client.list_files(DRIVE_FOLDER_ID)
        logger.info(f"Found {len(files)} files in folder {DRIVE_FOLDER_ID}.")

        backups = [f for f in files if f['name'].endswith('.json') or f['name'].startswith('TickerTracker')]
        histories = [f for f in files if f['name'].startswith('History_') and f['name'].endswith('.csv')]

        logger.info("Backup files:")
        for file in backups:
            logger.info(format_file_info(file))

        logger.info("History files:")
        for file in histories:
            logger.info(format_file_info(file))

        return backups, histories
    except Exception as e:
        logger.error(f"Failed to connect to Google Drive: {e}")
        raise

async def get_ticker_id_by_symbol(session, symbol):
    result = await session.execute(select(Ticker).where(Ticker.symbol == symbol))
    ticker = result.scalar_one_or_none()
    return ticker.id if ticker else None

async def download_and_import_files(backups, histories, estimate_repo, market_data_repo, session, dry_run):
    logger.info("Starting file download and import...")

    for backup in backups:
        logger.info(f"Processing backup file: {backup['name']}")
        try:
            content = await GoogleDriveClient.download_file(backup['id'])
            if backup['name'].endswith('.json'):
                data = LegacyJsonParser.parse(content)
            else:
                data = LegacyCsvParser.parse(content)

            tickers = set()
            for estimate in data:
                tickers.add(estimate['ticker'])
                if not dry_run:
                    await estimate_repo.insert_estimate(estimate)

            logger.info(f"Imported {len(data)} estimates, found {len(tickers)} unique tickers.")
        except Exception as e:
            logger.error(f"Failed to process backup file {backup['name']}: {e}")

    for history in histories:
        logger.info(f"Processing history file: {history['name']}")
        try:
            content = await GoogleDriveClient.download_file(history['id'])
            ticker_symbol = history['name'].split('_')[1].replace('.csv', '')
            data = LegacyCsvParser.parse_history_csv(content, default_ticker=ticker_symbol)

            if not dry_run:
                ticker_id = await get_ticker_id_by_symbol(session, ticker_symbol)
                if ticker_id is None:
                    logger.warning(f"Ticker symbol {ticker_symbol} not found in DB, skipping history import.")
                else:
                    await market_data_repo.upsert_daily(ticker_id, data)

            logger.info(f"Imported {len(data)} rows for ticker {ticker_symbol}.")
        except Exception as e:
            logger.error(f"Failed to process history file {history['name']}: {e}")

async def verify_consistency(estimate_repo, market_data_repo):
    logger.info("Verifying database consistency...")
    try:
        tickers_count = await estimate_repo.count_tickers()
        logger.info(f"Total tickers: {tickers_count}")

        top_estimates = await estimate_repo.get_top_estimates_by_ticker(10)
        logger.info("Top 10 tickers by estimates:")
        for ticker, count in top_estimates:
            logger.info(f"  {ticker}: {count} estimates")

        market_data_stats = await market_data_repo.get_market_data_stats()
        logger.info("Market data stats:")
        for ticker, stats in market_data_stats.items():
            logger.info(f"  {ticker}: {stats['days']} days, range {stats['min_date']} to {stats['max_date']}")

        estimates_without_market_data = await estimate_repo.get_estimates_without_market_data()
        logger.warning(f"Estimates without market data: {len(estimates_without_market_data)}")
    except Exception as e:
        logger.error(f"Consistency verification failed: {e}")

async def main(dry_run):
    drive_client = GoogleDriveClient()
    estimate_repo = EstimateRepository()
    market_data_repo = MarketDataRepository()

    async with AsyncSession() as session:
        try:
            backups, histories = await verify_google_drive(drive_client)
            await download_and_import_files(backups, histories, estimate_repo, market_data_repo, session, dry_run)
            await verify_consistency(estimate_repo, market_data_repo)
            if not dry_run:
                await session.commit()
        except Exception as e:
            logger.error(f"Error during migration and verification: {e}")
            await session.rollback()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrate and verify database from Google Drive backups.")
    parser.add_argument("--dry-run", action="store_true", help="Run the script without making changes to the database.")
    args = parser.parse_args()

    asyncio.run(main(args.dry_run))