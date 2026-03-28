import asyncio

import sqlalchemy as sa

from src.shared.infra.database import engine

tables = [
    'estimate_events', 'estimates', 'market_data', 'tickers', 'sync_jobs', 'users', 'roles'
]

def main():
    async def drop_all():
        async with engine.begin() as conn:
            meta = sa.MetaData()
            await conn.run_sync(meta.reflect)
            for table in tables:
                if table in meta.tables:
                    await conn.run_sync(lambda c: meta.tables[table].drop(c, checkfirst=True))
            print('✅ DB pulito')
    asyncio.run(drop_all())

if __name__ == "__main__":
    main()
