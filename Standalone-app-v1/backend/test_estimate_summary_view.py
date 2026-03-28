"""
Test script for estimate_summary_view materialized view.

This script:
1. Inserts sample data (tickers, market data, estimates)
2. Refreshes the materialized view
3. Queries the view to verify it works correctly
4. Tests query performance
"""

import asyncio
import os
import sys
import time
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from estimates.domain.entities import Direction, Estimate, EstimateStatus

# Import models
from market_data.domain.entities import Ticker
from market_data.domain.market_data import MarketData


async def create_sample_data(session: AsyncSession):
    """Create sample data for testing."""
    print("📦 Creating sample data...")

    # Create sample tickers
    ticker1 = Ticker(
        id=uuid.uuid4(),
        symbol="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD",
        asset_type="stock"
    )
    ticker2 = Ticker(
        id=uuid.uuid4(),
        symbol="TSLA",
        name="Tesla, Inc.",
        exchange="NASDAQ",
        currency="USD",
        asset_type="stock"
    )

    session.add_all([ticker1, ticker2])
    await session.flush()

    print(f"   ✓ Created tickers: {ticker1.symbol}, {ticker2.symbol}")

    # Create market data for the last 30 days
    today = date.today()
    for i in range(30, 0, -1):
        trade_date = today - timedelta(days=i)

        # AAPL data (trending up)
        apple_price = Decimal("150.00") + Decimal(str(i * 0.5))
        session.add(MarketData(
            ticker_id=ticker1.id,
            date=trade_date,
            open=apple_price,
            high=apple_price + Decimal("2.00"),
            low=apple_price - Decimal("1.50"),
            close=apple_price,
            volume=50000000 + (i * 100000),
            data_source="yahoo"
        ))

        # TSLA data (trending down)
        tesla_price = Decimal("300.00") - Decimal(str(i * 1.0))
        session.add(MarketData(
            ticker_id=ticker2.id,
            date=trade_date,
            open=tesla_price,
            high=tesla_price + Decimal("3.00"),
            low=tesla_price - Decimal("2.50"),
            close=tesla_price,
            volume=30000000 + (i * 50000),
            data_source="yahoo"
        ))

    await session.flush()
    print("   ✓ Created 30 days of market data for each ticker")

    # Create sample estimates
    # OPEN estimate - LONG on AAPL (profitable)
    estimate1 = Estimate(
        id=uuid.uuid4(),
        ticker_id=ticker1.id,
        start_price=Decimal("155.00"),
        target_price=Decimal("175.00"),
        stop_loss_price=Decimal("150.00"),
        target_profit_percent=Decimal("12.90"),
        stop_loss_percent=Decimal("3.23"),
        status=EstimateStatus.OPEN,
        direction=Direction.LONG,
        ai_model="gemini-1.5-pro",
        ai_confidence=Decimal("85.50"),
        ai_reasoning="Strong upward momentum, positive earnings",
        created_at=datetime.now() - timedelta(days=10),
        updated_at=datetime.now()
    )

    # OPEN estimate - SHORT on TSLA (losing)
    estimate2 = Estimate(
        id=uuid.uuid4(),
        ticker_id=ticker2.id,
        start_price=Decimal("290.00"),
        target_price=Decimal("260.00"),
        stop_loss_price=Decimal("310.00"),
        target_profit_percent=Decimal("10.34"),
        stop_loss_percent=Decimal("6.90"),
        status=EstimateStatus.OPEN,
        direction=Direction.SHORT,
        ai_model="gemini-1.5-pro",
        ai_confidence=Decimal("72.00"),
        ai_reasoning="Overvalued, expected correction",
        created_at=datetime.now() - timedelta(days=5),
        updated_at=datetime.now()
    )

    # CLOSED estimate - WIN
    estimate3 = Estimate(
        id=uuid.uuid4(),
        ticker_id=ticker1.id,
        start_price=Decimal("148.00"),
        target_price=Decimal("160.00"),
        stop_loss_price=Decimal("145.00"),
        target_profit_percent=Decimal("8.11"),
        stop_loss_percent=Decimal("2.03"),
        status=EstimateStatus.CLOSED_WIN,
        direction=Direction.LONG,
        ai_model="gemini-1.5-pro",
        ai_confidence=Decimal("90.00"),
        ai_reasoning="Technical breakout pattern",
        created_at=datetime.now() - timedelta(days=20),
        updated_at=datetime.now() - timedelta(days=2),
        closed_at=datetime.now() - timedelta(days=2),
        exit_price=Decimal("161.50"),
        realized_pnl=Decimal("1350.00")
    )

    session.add_all([estimate1, estimate2, estimate3])
    await session.commit()

    print("   ✓ Created 3 estimates (2 OPEN, 1 CLOSED)")
    print("\n✅ Sample data created successfully!")

    return ticker1, ticker2, estimate1, estimate2, estimate3


async def test_materialized_view(session: AsyncSession):
    """Test queries on the materialized view."""
    print("\n🔍 Testing materialized view queries...\n")

    # Test 1: Get all estimates from view
    print("📊 Test 1: Query all estimates")
    start_time = time.time()

    result = await session.execute(
        text("SELECT * FROM estimate_summary_view ORDER BY created_at DESC")
    )
    rows = result.fetchall()

    query_time = (time.time() - start_time) * 1000  # Convert to ms

    print(f"   Found {len(rows)} estimates")
    print(f"   Query time: {query_time:.2f} ms")

    for row in rows:
        print(f"\n   Estimate {row.id}:")
        print(f"      Status: {row.status}")
        print(f"      Direction: {row.direction}")
        print(f"      Start Price: ${row.start_price}")
        print(f"      Current Price: ${row.current_price}")
        print(f"      Current PnL: ${row.current_pnl:.2f}")
        print(f"      Current PnL %: {row.current_pnl_percent:.2f}%")
        print(f"      Days Open: {row.days_open}")
        print(f"      Risk Level: {row.risk_level}")

    # Test 2: Filter by status (OPEN estimates)
    print("\n📊 Test 2: Query OPEN estimates only")
    start_time = time.time()

    result = await session.execute(
        text("SELECT * FROM estimate_summary_view WHERE status = 'OPEN'")
    )
    open_estimates = result.fetchall()

    query_time = (time.time() - start_time) * 1000

    print(f"   Found {len(open_estimates)} open estimates")
    print(f"   Query time: {query_time:.2f} ms")

    # Test 3: Performance test - should be < 50ms
    print("\n📊 Test 3: Performance test (target < 50ms)")
    start_time = time.time()

    result = await session.execute(
        text("""
            SELECT status, COUNT(*) as count,
                   AVG(current_pnl_percent) as avg_pnl_percent
            FROM estimate_summary_view
            GROUP BY status
        """)
    )
    stats = result.fetchall()

    query_time = (time.time() - start_time) * 1000

    print(f"   Query time: {query_time:.2f} ms")
    print(f"   {'✅ PASS' if query_time < 50 else '⚠️  SLOW'} - Target is < 50ms")

    for stat in stats:
        print(f"   {stat.status}: {stat.count} estimates, Avg PnL: {stat.avg_pnl_percent:.2f}%")

    return query_time < 50


async def test_concurrent_refresh():
    """Test REFRESH MATERIALIZED VIEW CONCURRENTLY."""
    print("\n🔄 Testing concurrent refresh...")

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev"
    )

    engine: AsyncEngine = create_async_engine(database_url, echo=False)

    try:
        async with engine.connect() as conn:
            start_time = time.time()

            await conn.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY estimate_summary_view"))
            await conn.commit()

            refresh_time = (time.time() - start_time) * 1000

            print("   ✅ Concurrent refresh successful")
            print(f"   Refresh time: {refresh_time:.2f} ms")

    except Exception as e:
        print(f"   ❌ Concurrent refresh failed: {e}")
        return False

    finally:
        await engine.dispose()

    return True


async def main():
    """Main test function."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://tickertracker:devpassword@localhost:5432/tickertracker_dev"
    )

    engine: AsyncEngine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("=" * 80)
    print("ESTIMATE SUMMARY VIEW - TEST SCRIPT")
    print("=" * 80)

    try:
        async with async_session() as session:
            # Create sample data
            await create_sample_data(session)

            # Refresh the materialized view
            print("\n🔄 Refreshing materialized view...")
            async with engine.connect() as conn:
                await conn.execute(text("REFRESH MATERIALIZED VIEW estimate_summary_view"))
                await conn.commit()
            print("   ✅ View refreshed")

            # Test the view
            await test_materialized_view(session)

        # Test concurrent refresh
        refresh_ok = await test_concurrent_refresh()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!" if refresh_ok else "⚠️  SOME TESTS FAILED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        await engine.dispose()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
