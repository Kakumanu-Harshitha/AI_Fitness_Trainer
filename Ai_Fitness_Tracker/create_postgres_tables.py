import asyncio
from backend.app.db.database import async_engine, Base
from backend.app.db.models import User, WorkoutLog, WorkoutPlan, FriendActivity # Import all models

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
