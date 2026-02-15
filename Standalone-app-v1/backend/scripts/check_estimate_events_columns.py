import sqlalchemy as sa
import asyncio
from src.shared.infra.database import engine

def main():
    async def check():
        async with engine.connect() as conn:
            def sync_check(sync_conn):
                insp = sa.inspect(sync_conn)
                cols = insp.get_columns('estimate_events')
                print([(c['name'], str(c['type'])) for c in cols])
            await conn.run_sync(sync_check)
    asyncio.run(check())

if __name__ == "__main__":
    main()
