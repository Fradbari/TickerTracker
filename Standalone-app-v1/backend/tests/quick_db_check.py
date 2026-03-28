import asyncio

import sqlalchemy as sa

from src.shared.infra.database import engine


async def main():
    async with engine.connect() as conn:
        print("\n== Conteggio record per tabella ==")
        for table in ["tickers", "estimates", "market_data", "estimate_events", "sync_jobs"]:
            result = await conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"{table}: {count}")

        print("\n== Esempio dati estimates ==")
        res = await conn.execute(sa.text("SELECT id, ticker_id, start_price, created_at FROM estimates ORDER BY created_at DESC LIMIT 5"))
        for row in res.fetchall():
            print(dict(row._mapping))

        print("\n== Esempio dati market_data ==")
        res = await conn.execute(sa.text("SELECT ticker_id, date, open, high, low, close FROM market_data ORDER BY date DESC LIMIT 5"))
        for row in res.fetchall():
            print(dict(row._mapping))

if __name__ == "__main__":
    asyncio.run(main())
