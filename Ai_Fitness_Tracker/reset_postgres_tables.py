import asyncio
import sys
import os

# Add the current directory to sys.path so we can import backend
sys.path.append(os.getcwd())

from backend.app.db.database import async_engine, Base
from backend.app.db.models import User, WorkoutLog, WorkoutPlan, FriendActivity, Routine, RoutineStep, Friendship, Badge, UserBadge, FriendActivity, WaterLog # Import all models

async def reset_tables():
    print("Connecting to database to reset tables...")
    async with async_engine.begin() as conn:
        # Drop all tables
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables reset and recreated successfully!")

if __name__ == "__main__":
    asyncio.run(reset_tables())
