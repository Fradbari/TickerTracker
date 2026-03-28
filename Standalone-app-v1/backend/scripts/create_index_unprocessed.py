import asyncio

import sqlalchemy as sa

from src.shared.infra.database import engine


def main():
    async def create_index():
        async with engine.connect() as conn:
            try:
                await conn.execute(sa.text("""
                    CREATE INDEX ix_estimate_events_unprocessed ON estimate_events (processed_at);
                """))
                await conn.commit()
                print("✅ Indice creato con successo")
            except Exception as e:
                print(f"❌ Errore nella creazione dell'indice: {e}")
    asyncio.run(create_index())

if __name__ == "__main__":
    main()
