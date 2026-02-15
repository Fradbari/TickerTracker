import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database connection settings
DATABASE_URL = os.getenv("DATABASE_URL")
EXPECTED_TABLES = ["estimates", "estimate_events", "tickers", "daily_candles", "sync_jobs"]

def format_status(exists):
    return "✅" if exists else "❌"

async def verify_database():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env")
        return

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # Test connection
        try:
            await conn.execute(text("SELECT 1"))
            print("Database connection: ✅")
        except Exception as e:
            print(f"Database connection: ❌ ({e})")
            return

        # Check database existence
        db_name = DATABASE_URL.split("/")[-1]
        result = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        db_exists = result.scalar() is not None
        print(f"Database '{db_name}': {format_status(db_exists)}")

        if not db_exists:
            return

        # List tables and count records
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        print("\nTables:")
        for table in EXPECTED_TABLES:
            if table in tables:
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"  {table}: {format_status(True)} ({count} records)")
            else:
                print(f"  {table}: {format_status(False)}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_database())