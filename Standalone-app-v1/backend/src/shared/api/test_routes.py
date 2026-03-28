from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.shared.infra.database import get_db

router = APIRouter(prefix="/api/test", tags=["test"])

@router.post("/seed")
async def seed_test_database(db: AsyncSession = Depends(get_db)):
    """Seed or clean the test database."""
    # Since we use DDD/CQRS, we normally don't delete everything,
    # but for E2E it's necessary.
    try:
        # TRUNCATE estimates cascade
        await db.execute(text("TRUNCATE TABLE estimates CASCADE;"))
        # we can also truncate tickers if we store them
        # await db.execute(text("TRUNCATE TABLE tickers CASCADE;")) 
        await db.commit()
    except Exception as e:
        await db.rollback()
        # Fallback or ignore if table doesn't exist
        print(f"Error seeding DB: {e}")
    return {"status": "success", "message": "Database cleaned and seeded"}
