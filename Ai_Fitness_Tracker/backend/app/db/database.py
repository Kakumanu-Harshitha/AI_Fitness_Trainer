from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

# Async database setup
ASYNC_DATABASE_URL = settings.get_database_url(is_async=True)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Sync database setup (for Alembic or special sync tasks)
SYNC_DATABASE_URL = settings.get_database_url(is_async=False)
if SYNC_DATABASE_URL.startswith("sqlite"):
    sync_engine = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
else:
    sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

Base = declarative_base()

# Dependency for FastAPI
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
