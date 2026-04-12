"""
Migrate and Verify - Import legacy data from Google Drive to local database.

This script:
1. Lists all files in Google Drive folder
2. Downloads and imports backup JSON/CSV files (estimates)
3. Downloads and imports History_*.csv files (market data)
4. Verifies data consistency and reports statistics

Usage:
    python scripts/migrate_and_verify.py              # Full import
    python scripts/migrate_and_verify.py --dry-run    # Preview without changes
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.estimates.domain.entities import Direction, Estimate, EstimateStatus
from src.infra.drive.client import GoogleDriveClient
from src.infra.drive.models import DriveFile
from src.market_data.domain.entities import Ticker
from src.market_data.domain.market_data import MarketData
from src.shared.infra.config import get_settings
from src.shared.infra.database import AsyncSessionLocal
from src.sync.infra.csv_parser import LegacyCsvParser
from src.sync.infra.json_parser import LegacyJsonParser
from src.sync.infra.legacy_models import LegacyEstimateRow, LegacyHistoryRow
from src.market_data.services.market_data_service import MarketDataService
from src.market_data.services.yahoo_provider import YahooMarketDataProvider
from src.market_data.repositories.market_data_repository import MarketDataRepository
from sqlalchemy import select

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationStats:
    """Track migration statistics."""
    def __init__(self):
        self.backup_files_found = 0
        self.history_files_found = 0
        self.estimates_imported = 0
        self.estimates_skipped = 0
        self.estimates_price_corrected = 0
        self.tickers_created = 0
        self.market_data_imported = 0
        self.market_data_skipped = 0
        self.errors: list[str] = []


async def verify_google_drive(drive_client: GoogleDriveClient, folder_id: str) -> tuple[list[DriveFile], list[DriveFile]]:
    """
    List and categorize files in Google Drive folder.

    Returns:
        Tuple of (backup_files, history_files)
    """
    logger.info("=" * 60)
    logger.info("FASE 1: VERIFICA GOOGLE DRIVE")
    logger.info("=" * 60)

    try:
        files = await drive_client.list_files(folder_id)
        logger.info(f"✅ Trovati {len(files)} file nella cartella")

        # Categorize files
        backups = []
        histories = []

        for file in files:
            # Escludi debug_logs.json dai backup
            if file.name == "debug_logs.json":
                logger.info(f"  ⏭️  Escluso {file.name} dalla migrazione")
                continue
            # Backup files: JSON or CSV (not history)
            if file.name.endswith('.json') or (file.name.endswith('.csv') and 'history' not in file.name.lower()):
                backups.append(file)
                size_kb = (file.size or 0) // 1024
                mod_time = file.modified_time.strftime('%Y-%m-%d %H:%M') if file.modified_time else 'N/A'
                logger.info(f"  📄 {file.name} ({size_kb} KB, modificato {mod_time})")
            # History files
            elif 'history' in file.name.lower() and file.name.endswith('.csv'):
                histories.append(file)
                # Pattern can be History_ORCL.csv or ORCL_History.csv
                ticker = file.name.lower().replace('history', '').replace('_', '').replace('.csv', '').upper()
                size_kb = (file.size or 0) // 1024
                logger.info(f"  📈 {file.name} - Ticker: {ticker} ({size_kb} KB)")

        logger.info(f"\nTotale: {len(backups)} backup, {len(histories)} history files\n")
        return backups, histories

    except Exception as e:
        logger.error(f"❌ Errore connessione Google Drive: {e}")
        raise


async def get_or_create_ticker(session: AsyncSession, symbol: str, stats: MigrationStats) -> Ticker:
    """Get existing ticker or create new one."""
    result = await session.execute(
        text("SELECT id, symbol, name, exchange, currency, asset_type FROM tickers WHERE symbol = :symbol"),
        {"symbol": symbol.upper()}
    )
    row = result.fetchone()

    if row:
        ticker = Ticker()
        ticker.id = row[0]
        ticker.symbol = row[1]
        ticker.name = row[2]
        ticker.exchange = row[3]
        ticker.currency = row[4]
        ticker.asset_type = row[5]
        return ticker

    # Create new ticker
    new_ticker = Ticker(
        symbol=symbol.upper(),
        name=symbol.upper(),  # Can be updated later
        exchange="UNKNOWN",
        currency="USD",
        asset_type="stock"  # Default to stock
    )
    session.add(new_ticker)
    await session.flush()  # Get ID without committing
    stats.tickers_created += 1
    logger.debug(f"  ➕ Created new ticker: {symbol}")
    return new_ticker


async def get_latest_price_for_ticker(
    session: AsyncSession,
    ticker_id: str,
    before_date: datetime
) -> Decimal | None:
    """
    Get the latest available price for a ticker from market_data.

    Args:
        session: Database session
        ticker_id: UUID of the ticker
        before_date: Get price before or on this date

    Returns:
        Latest close price as Decimal, or None if no data available
    """
    try:
        result = await session.execute(
            text("""
                SELECT close FROM market_data
                WHERE ticker_id = :ticker_id
                AND date <= :before_date
                ORDER BY date DESC
                LIMIT 1
            """),
            {
                "ticker_id": ticker_id,
                "before_date": before_date.date()
            }
        )
        row = result.fetchone()
        return Decimal(str(row[0])) if row else None
    except Exception as e:
        logger.debug(f"Could not fetch latest price: {e}")
        return None


async def import_estimate_row(
    session: AsyncSession,
    row: LegacyEstimateRow,
    stats: MigrationStats,
    dry_run: bool,
    source_file: str = None,
    row_idx: int = None
) -> None:
    """Import a single estimate from legacy format."""
    try:
        # Validazione ticker
        file_info = f"file={source_file}" if source_file else "file=UNKNOWN"
        row_info = f"row={row_idx}" if row_idx is not None else "row=?"
        if not row.ticker or row.ticker.strip().upper() == "UNKNOWN":
            error_msg = (
                f"Cannot import row: missing or UNKNOWN ticker (start_date={row.start_date}, price={row.start_price}, {file_info}, {row_info})"
            )
            logger.error(f"  ❌ {error_msg}")
            stats.errors.append(error_msg)
            return

        # Get or create ticker
        ticker = await get_or_create_ticker(session, row.ticker, stats)

        # Check if estimate already exists (by ticker + start_date + start_price)
        # BUT: if start_price=0, we can't use it for deduplication, so check without it
        if row.start_price > 0:
            result = await session.execute(
                text("""
                    SELECT COUNT(*) FROM estimates
                    WHERE ticker_id = :ticker_id
                    AND DATE(created_at) = :start_date
                    AND ABS(start_price - :start_price) < 0.01
                """),
                {
                    "ticker_id": str(ticker.id),
                    "start_date": row.start_date,
                    "start_price": float(row.start_price)
                }
            )
        else:
            # If start_price=0, check by ticker + date only
            result = await session.execute(
                text("""
                    SELECT COUNT(*) FROM estimates
                    WHERE ticker_id = :ticker_id
                    AND DATE(created_at) = :start_date
                """),
                {
                    "ticker_id": str(ticker.id),
                    "start_date": row.start_date
                }
            )

        exists = result.scalar() > 0

        if exists:
            stats.estimates_skipped += 1
            logger.debug(f"  ⏭️  Skipped {row.ticker} (already exists)")
            return

        # ===== HANDLE start_price = 0 =====
        corrected_start_price = row.start_price
        price_correction_method = None

        if row.start_price <= 0:
            logger.warning(f"  ⚠️  {row.ticker}: start_price = {row.start_price}, attempting correction... ({file_info}, {row_info})")

            # Try 1: Get latest market_data price before start_date
            created_at = datetime.combine(row.start_date, datetime.min.time())
            latest_price = await get_latest_price_for_ticker(session, str(ticker.id), created_at)

            if latest_price and latest_price > 0:
                corrected_start_price = latest_price
                price_correction_method = f"market_data (latest: {latest_price})"

            # Try 2: Use target_price if available and positive
            elif row.target_price and row.target_price > 0:
                corrected_start_price = row.target_price
                price_correction_method = f"target_price ({row.target_price})"

            # Try 3: Use stop_loss_price if available and positive
            elif row.stop_loss_price and row.stop_loss_price > 0:
                corrected_start_price = row.stop_loss_price
                price_correction_method = f"stop_loss_price ({row.stop_loss_price})"

            # Try 4: Use current_price if available
            elif row.current_price and row.current_price > 0:
                corrected_start_price = row.current_price
                price_correction_method = f"current_price ({row.current_price})"

            # Give up: can't find valid price
            else:
                error_msg = (
                    f"Cannot import {row.ticker} (start_date={row.start_date}): start_price=0 and no valid fallback price found ({file_info}, {row_info})"
                )
                logger.error(f"  ❌ {error_msg}")
                stats.errors.append(error_msg)
                return

            # Log the correction
            logger.info(
                f"  🔧 {row.ticker}: Corrected start_price from {row.start_price} to {corrected_start_price} "
                f"using {price_correction_method}"
            )
            stats.estimates_price_corrected += 1

        if not dry_run:
            # Map legacy status to new status enum
            try:
                status = EstimateStatus[row.status] if row.status else EstimateStatus.OPEN
            except KeyError:
                logger.warning(f"  ⚠️  Unknown status '{row.status}' for {row.ticker}, defaulting to OPEN")
                status = EstimateStatus.OPEN

            # Map direction
            try:
                direction = Direction[row.direction] if row.direction else Direction.LONG
            except KeyError:
                logger.warning(f"  ⚠️  Unknown direction '{row.direction}' for {row.ticker}, defaulting to LONG")
                direction = Direction.LONG

            # Calculate realized_pnl from percent if available and not set
            realized_pnl = row.realized_pnl
            if realized_pnl is None and row.realized_pnl_percent and corrected_start_price:
                realized_pnl = corrected_start_price * (row.realized_pnl_percent / Decimal("100"))

            # Recalculate target/stop prices if they were 0
            final_target_price = row.target_price
            final_stop_loss_price = row.stop_loss_price

            if final_target_price <= 0 and row.target_profit_percent and corrected_start_price > 0:
                final_target_price = corrected_start_price * (1 + row.target_profit_percent / Decimal("100"))

            if final_stop_loss_price <= 0 and row.stop_loss_percent and corrected_start_price > 0:
                final_stop_loss_price = corrected_start_price * (1 + row.stop_loss_percent / Decimal("100"))

            # Create estimate
            estimate = Estimate(
                ticker_id=ticker.id,
                start_price=corrected_start_price,  # ✅ Use corrected price
                target_price=final_target_price,
                stop_loss_price=final_stop_loss_price,
                target_profit_percent=row.target_profit_percent,
                stop_loss_percent=row.stop_loss_percent,
                direction=direction,
                status=status,
                ai_model=row.ai_model,
                ai_confidence=row.ai_confidence,
                exit_price=row.exit_price,
                realized_pnl=realized_pnl,
                realized_pnl_percent=row.realized_pnl_percent,
                created_at=datetime.combine(row.start_date, datetime.min.time()),
                closed_at=datetime.combine(row.close_date, datetime.min.time()) if row.close_date else None,
            )
            session.add(estimate)

        stats.estimates_imported += 1

    except Exception as e:
        error_msg = f"Errore import estimate {getattr(row, 'ticker', 'UNKNOWN')}: {e} ({file_info}, {row_info})"
        logger.warning(f"⚠️  {error_msg}")
        stats.errors.append(error_msg)


async def import_history_rows(
    session: AsyncSession,
    ticker_symbol: str,
    rows: list[LegacyHistoryRow],
    stats: MigrationStats,
    dry_run: bool
) -> None:
    """Import historical market data for a ticker."""
    try:
        # Get ticker
        ticker = await get_or_create_ticker(session, ticker_symbol, stats)

        imported = 0
        skipped = 0

        if not dry_run:
            for row in rows:
                # Check if data already exists
                result = await session.execute(
                    text("SELECT COUNT(*) FROM market_data WHERE ticker_id = :ticker_id AND date = :date"),
                    {"ticker_id": str(ticker.id), "date": row.date}
                )
                exists = result.scalar() > 0
                if exists:
                    skipped += 1
                    continue

                # Forza high = open se high < open
                high_value = row.high
                if row.high is not None and row.open is not None and row.high < row.open:
                    logger.warning(f"  ⚠️  {ticker_symbol} {row.date}: high ({row.high}) < open ({row.open}), forzo high = open")
                    high_value = row.open

                # Forza low = open se low > open
                low_value = row.low
                if row.low is not None and row.open is not None and row.low > row.open:
                    logger.warning(f"  ⚠️  {ticker_symbol} {row.date}: low ({row.low}) > open ({row.open}), forzo low = open")
                    low_value = row.open

                # Forza low = close se low > close

                if row.low is not None and row.close is not None and low_value > row.close:
                    logger.warning(f"  ⚠️  {ticker_symbol} {row.date}: low ({low_value}) > close ({row.close}), forzo low = close")
                    low_value = row.close

                # Forza high = close se high < close
                if high_value is not None and row.close is not None and high_value < row.close:
                    logger.warning(f"  ⚠️  {ticker_symbol} {row.date}: high ({high_value}) < close ({row.close}), forzo high = close")
                    high_value = row.close

                # Forza high = close se high < close
                if high_value is not None and row.close is not None and high_value < row.close:
                    logger.warning(f"  ⚠️  {ticker_symbol} {row.date}: high ({high_value}) < close ({row.close}), forzo high = close")
                    high_value = row.close

                # Insert market data
                market_data = MarketData(
                    ticker_id=ticker.id,
                    date=row.date,
                    open=row.open,
                    high=high_value,
                    low=low_value,
                    close=row.close,
                    volume=row.volume,
                    data_source="legacy_import",
                    quality_score=Decimal("0.80")
                )
                session.add(market_data)
                imported += 1
        else:
            imported = len(rows)

        stats.market_data_imported += imported
        stats.market_data_skipped += skipped

        logger.info(f"  ✅ {ticker_symbol}: {imported} giorni importati, {skipped} skippati")

    except Exception as e:
        error_msg = f"Errore import history {ticker_symbol}: {e}"
        logger.warning(f"⚠️  {error_msg}")
        stats.errors.append(error_msg)


async def download_and_import(
    drive_client: GoogleDriveClient,
    backups: list[DriveFile],
    histories: list[DriveFile],
    session: AsyncSession,
    stats: MigrationStats,
    dry_run: bool
) -> None:
    """Download and import all files."""
    logger.info("=" * 60)
    logger.info("FASE 2: IMPORT DATI")
    logger.info("=" * 60)

    # Initialize parsers
    json_parser = LegacyJsonParser()
    csv_parser = LegacyCsvParser()

    # IMPORTANT: Import history files FIRST so market_data is available for price corrections
    if histories:
        logger.info(f"\n📈 History Files ({len(histories)}) - Importing FIRST for price fallback:")
        for history_file in histories:
            try:
                # Extract ticker from filename broadly
                ticker_symbol = history_file.name.lower().replace('history', '').replace('_', '').replace('.csv', '').upper()

                # Download and parse
                content = await drive_client.download_file(history_file.id)
                rows = csv_parser.parse_history_csv(content, default_ticker=ticker_symbol)

                # Import history
                await import_history_rows(session, ticker_symbol, rows, stats, dry_run)

                stats.history_files_found += 1

            except Exception as e:
                error_msg = f"Errore processing history {history_file.name}: {e}"
                logger.error(f"❌ {error_msg}")
                stats.errors.append(error_msg)

        logger.info("\n✅ History import completato:")
        logger.info(f"  • {stats.market_data_imported} record importati")
        logger.info(f"  • {stats.market_data_skipped} record skippati")
    else:
        logger.warning("⚠️  Nessun file history trovato!")

    # Import backup files AFTER history (so we have market_data for fallback)
    if backups:
        logger.info(f"\n📊 Backup Files ({len(backups)}):")
        for backup_file in backups:
            logger.info(f"\n📥 Processing: {backup_file.name}")

            try:
                # Download file
                content = await drive_client.download_file(backup_file.id)

                # Parse based on file type
                if backup_file.name.endswith('.json'):
                    rows = json_parser.parse_backup_json(content.decode('utf-8'))
                else:
                    rows = csv_parser.parse_estimates_csv(content)

                logger.info(f"  📊 Trovate {len(rows)} estimates nel file")

                # Import each estimate
                for idx, row in enumerate(rows):
                    await import_estimate_row(session, row, stats, dry_run, source_file=backup_file.name, row_idx=idx+1)

                stats.backup_files_found += 1

            except Exception as e:
                error_msg = f"Errore processing backup {backup_file.name}: {e}"
                logger.error(f"❌ {error_msg}")
                stats.errors.append(error_msg)

        logger.info("\n✅ Backup import completato:")
        logger.info(f"  • {stats.estimates_imported} stime importate")
        logger.info(f"  • {stats.estimates_skipped} stime skippate (già presenti)")
        logger.info(f"  • {stats.estimates_price_corrected} stime con prezzo corretto")
        logger.info(f"  • {stats.tickers_created} nuovi ticker creati")
    else:
        logger.warning("⚠️  Nessun file backup trovato!")


async def verify_consistency(session: AsyncSession) -> None:
    """Verify database consistency and report statistics."""
    logger.info("\n" + "=" * 60)
    logger.info("FASE 3: VERIFICA CONSISTENZA")
    logger.info("=" * 60 + "\n")

    # Count records
    counts = {}
    for table in ["tickers", "estimates", "estimate_events", "market_data", "sync_jobs"]:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        counts[table] = result.scalar()

    logger.info("Database Status:")
    for table, count in counts.items():
        logger.info(f"  • {table:20s}: {count:>6,} records")

    # Top tickers by estimates
    result = await session.execute(text("""
        SELECT t.symbol, COUNT(e.id) as estimate_count
        FROM tickers t
        LEFT JOIN estimates e ON e.ticker_id = t.id
        GROUP BY t.id, t.symbol
        HAVING COUNT(e.id) > 0
        ORDER BY estimate_count DESC
        LIMIT 10
    """))

    rows = result.fetchall()
    if rows:
        logger.info("\nTop 10 Tickers per Estimates:")
        for row in rows:
            logger.info(f"  {row[0]:10s}: {row[1]:>3} stime")

    # Market data coverage
    result = await session.execute(text("""
        SELECT
            t.symbol,
            COUNT(md.date) as days_of_data,
            MIN(md.date) as first_date,
            MAX(md.date) as last_date
        FROM tickers t
        INNER JOIN estimates e ON e.ticker_id = t.id
        LEFT JOIN market_data md ON md.ticker_id = t.id
        GROUP BY t.id, t.symbol
        HAVING COUNT(e.id) > 0
        ORDER BY days_of_data DESC
        LIMIT 10
    """))

    rows = result.fetchall()
    if rows:
        logger.info("\nCopertura Market Data (Top 10 ticker con stime):")
        warnings = []
        for row in rows:
            symbol, days, first_date, last_date = row
            if days == 0:
                warnings.append(symbol)
                logger.info(f"  ⚠️  {symbol:10s}: NESSUN DATO STORICO!")
            else:
                logger.info(f"  ✅ {symbol:10s}: {days:>4} giorni ({first_date} → {last_date})")

        if warnings:
            logger.warning(f"\n⚠️  {len(warnings)} ticker con stime ma SENZA market data: {', '.join(warnings)}")
        else:
            logger.info("\n✅ Tutti i ticker con stime hanno market data")


async def main(dry_run: bool = False):
    """Main migration workflow."""
    # Load settings
    settings = get_settings()

    # Initialize stats
    stats = MigrationStats()

    # Initialize Drive client
    drive_client = GoogleDriveClient(
        service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON.get_secret_value(),
        timeout=30
    )

    start_time = datetime.now()
    logger.info(f"\n{'=' * 60}")
    logger.info(f"MIGRATE AND VERIFY - {'DRY RUN MODE' if dry_run else 'LIVE MODE'}")
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"{'=' * 60}\n")

    try:
        # Verify Drive files
        backups, histories = await verify_google_drive(drive_client, settings.DRIVE_FOLDER_ID)

        # Import data
        async with AsyncSessionLocal() as session:
            try:
                await download_and_import(drive_client, backups, histories, session, stats, dry_run)

                if not dry_run:
                    await session.commit()
                    logger.info("\n✅ Transazione committata")
                    
                    # -----------------------------------------------------
                    # FETCH MISSING HISTORICAL DATA FROM YAHOO FINANCE
                    # -----------------------------------------------------
                    logger.info("\n" + "=" * 60)
                    logger.info("FASE 2.5: SYNC STORICO CANDELE DA YAHOO")
                    logger.info("=" * 60 + "\n")
                    
                    from datetime import date
                    from src.market_data.services.yahoo_provider import YahooMarketDataProvider
                    from src.market_data.repositories.market_data_repository import MarketDataRepository
                    from src.market_data.services.market_data_service import MarketDataService
                    
                    provider = YahooMarketDataProvider()
                    repository = MarketDataRepository()
                    md_service = MarketDataService(provider, repository, AsyncSessionLocal)
                    
                    async with AsyncSessionLocal() as md_session:
                        result = await md_session.execute(select(Ticker))
                        all_tickers = result.scalars().all()
                        
                        start_d = date(2020, 1, 1)
                        end_d = date.today()
                        
                        for t in all_tickers:
                            logger.info(f"Scarico storico da {start_d} a {end_d} per il ticker: {t.symbol} ...")
                            try:
                                count = await md_service.sync_historical_data(
                                    ticker_id=t.id,
                                    start_date=start_d,
                                    end_date=end_d,
                                    interval="1d"
                                )
                                logger.info(f"  ✅ {count} candele salvate per {t.symbol}")
                            except Exception as e:
                                logger.error(f"  ❌ Errore scaricamento {t.symbol}: {e}")
                else:
                    await session.rollback()
                    logger.info("\n🔍 DRY RUN: Nessuna modifica al database")

                # Verify consistency (in separate read-only session)
                async with AsyncSessionLocal() as verify_session:
                    await verify_consistency(verify_session)

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Errore durante import: {e}")
                raise

    except Exception as e:
        logger.error(f"❌ Errore fatale: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Final report
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("\n" + "=" * 60)
        logger.info("RIEPILOGO FINALE")
        logger.info("=" * 60)
        logger.info(f"\nTempo esecuzione: {duration:.2f}s")
        logger.info("\nFile processati:")
        logger.info(f"  • {stats.backup_files_found} backup files")
        logger.info(f"  • {stats.history_files_found} history files")
        logger.info("\nTickers:")
        logger.info(f"  • {stats.tickers_created} nuovi ticker creati")
        logger.info("\nEstimates:")
        logger.info(f"  • {stats.estimates_imported} importate")
        logger.info(f"  • {stats.estimates_skipped} skippate (già presenti)")
        logger.info(f"  • {stats.estimates_price_corrected} con start_price corretto")
        logger.info("\nMarket Data:")
        logger.info(f"  • {stats.market_data_imported} record importati")
        logger.info(f"  • {stats.market_data_skipped} skippati (già presenti)")

        if stats.errors:
            logger.warning(f"\n⚠️  {len(stats.errors)} errori durante l'import:")
            for error in stats.errors[:10]:  # Show first 10
                logger.warning(f"  • {error}")
            if len(stats.errors) > 10:
                logger.warning(f"  ... e altri {len(stats.errors) - 10} errori")
        else:
            logger.info("\n✅ Import completato senza errori")

        logger.info("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate legacy data from Google Drive to local database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview import without making changes to database"
    )
    args = parser.parse_args()

    exit_code = asyncio.run(main(dry_run=args.dry_run))
    exit(exit_code)
