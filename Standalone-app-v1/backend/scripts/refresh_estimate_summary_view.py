"""
Script to refresh the estimate_summary_view materialized view.

This script performs a CONCURRENT refresh of the materialized view,
which allows queries to continue reading the view while it's being refreshed.

The CONCURRENT option requires a unique index on the view (which we have on 'id').
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


async def refresh_estimate_summary_view(concurrent: bool = True):
    """
    Refresh the estimate_summary_view materialized view.

    Args:
        concurrent: If True, uses REFRESH MATERIALIZED VIEW CONCURRENTLY
                   (allows concurrent reads). If False, uses exclusive lock.

    Returns:
        True if successful, False otherwise
    """
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev"
    )

    engine: AsyncEngine = create_async_engine(database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Use CONCURRENTLY to avoid locking the view
            refresh_sql = (
                "REFRESH MATERIALIZED VIEW CONCURRENTLY estimate_summary_view"
                if concurrent
                else "REFRESH MATERIALIZED VIEW estimate_summary_view"
            )

            print(f"🔄 Refreshing materialized view {'(CONCURRENTLY)' if concurrent else '(with lock)'}...")

            await conn.execute(text(refresh_sql))
            await conn.commit()

            print("✅ Materialized view refreshed successfully!")
            return True

    except Exception as e:
        print(f"❌ Error refreshing materialized view: {e}")
        return False

    finally:
        await engine.dispose()


async def get_view_stats():
    """Get statistics about the materialized view."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev"
    )

    engine: AsyncEngine = create_async_engine(database_url, echo=False)

    try:
        async with engine.connect() as conn:
            # Get row count
            result = await conn.execute(text("SELECT COUNT(*) as count FROM estimate_summary_view"))
            row_count = (await result.fetchone())[0]

            # Get open estimates count
            result = await conn.execute(
                text("SELECT COUNT(*) as count FROM estimate_summary_view WHERE status = 'OPEN'")
            )
            open_count = (await result.fetchone())[0]

            print("\n📊 Materialized View Statistics:")
            print(f"   Total estimates: {row_count}")
            print(f"   Open estimates: {open_count}")
            print(f"   Closed estimates: {row_count - open_count}")

    except Exception as e:
        print(f"❌ Error getting view statistics: {e}")

    finally:
        await engine.dispose()


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Refresh the estimate_summary_view materialized view"
    )
    parser.add_argument(
        "--no-concurrent",
        action="store_true",
        help="Disable concurrent refresh (faster but locks the view)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics after refresh"
    )

    args = parser.parse_args()

    # Refresh the view
    success = await refresh_estimate_summary_view(concurrent=not args.no_concurrent)

    # Show statistics if requested
    if success and args.stats:
        await get_view_stats()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
