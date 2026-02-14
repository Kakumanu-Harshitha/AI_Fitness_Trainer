import asyncio
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

# Mock Redis BEFORE importing app or as early as possible
from app.core.redis import redis_service
redis_service.connect = AsyncMock()
redis_service.disconnect = AsyncMock()
redis_service.get = AsyncMock(return_value=None)
redis_service.set = AsyncMock()
redis_service.incr = AsyncMock(return_value=1)
redis_service.delete = AsyncMock()

from app.main import app as fastapi_app
from app.db.database import Base, get_async_db
from app.api.dependencies import get_db

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

fastapi_app.dependency_overrides[get_db] = override_get_db
fastapi_app.dependency_overrides[get_async_db] = override_get_db

# Patch AsyncSessionLocal in various modules to use the test engine
import app.db.database as db_mod
import app.api.v1.websockets as ws_mod
db_mod.AsyncSessionLocal = TestingSessionLocal
ws_mod.AsyncSessionLocal = TestingSessionLocal

from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def client():
    # Create tables on the async engine
    # We need a trick to run async code in a sync fixture
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    loop.run_until_complete(create_tables())
    
    with TestClient(fastapi_app) as c:
        yield c
    
    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    loop.run_until_complete(drop_tables())

@pytest_asyncio.fixture(scope="module")
async def async_client():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Use ASGITransport to avoid deprecation warnings and ensure proper async handling
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
