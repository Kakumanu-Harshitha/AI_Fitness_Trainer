import redis.asyncio as redis
from ..core.config import settings
import json
import time
from typing import Optional, Any, Dict

class RedisService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._memory_storage: Dict[str, Any] = {}
        self._memory_expiries: Dict[str, float] = {}

    async def connect(self):
        # Only try once to avoid log spam if it fails
        if hasattr(self, '_attempted_connect') and self._attempted_connect:
            return
        self._attempted_connect = True
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=0.5, # Slightly more time for initial connect
                socket_timeout=0.5
            )
            # Ping to verify connection
            await self.redis_client.ping()
            print("✅ Connected to Redis successfully")
        except Exception:
            # Silence the error to avoid log spam
            self.redis_client = None
            print("ℹ️ Redis not available. Using in-memory fallback for rate limiting.")

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def set(self, key: str, value: Any, expire: int = 3600):
        if self.redis_client:
            try:
                await self.redis_client.set(key, json.dumps(value), ex=expire)
                return
            except:
                pass
        
        # In-memory fallback
        self._memory_storage[key] = value
        self._memory_expiries[key] = time.time() + expire

    async def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
            except:
                pass
        
        # In-memory fallback
        if key in self._memory_storage:
            if time.time() < self._memory_expiries.get(key, 0):
                return self._memory_storage[key]
            else:
                # Expired
                del self._memory_storage[key]
                if key in self._memory_expiries:
                    del self._memory_expiries[key]
        return None

    async def delete(self, key: str):
        if self.redis_client:
            try:
                await self.redis_client.delete(key)
                return
            except:
                pass
        
        # In-memory fallback
        self._memory_storage.pop(key, None)
        self._memory_expiries.pop(key, None)

    async def incr(self, key: str):
        if self.redis_client:
            try:
                await self.redis_client.incr(key)
                return
            except:
                pass
        
        # In-memory fallback
        current = await self.get(key)
        if current is None:
            await self.set(key, 1)
        else:
            try:
                new_val = int(current) + 1
                self._memory_storage[key] = new_val
            except:
                self._memory_storage[key] = 1

redis_service = RedisService()
