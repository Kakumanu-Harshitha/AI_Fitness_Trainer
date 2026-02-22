import redis
import sys
import os

sys.path.append(os.getcwd())
from backend.app.core.config import settings

try:
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        socket_timeout=2
    )
    r.ping()
    print("Redis is reachable.")
except Exception as e:
    print(f"Redis is NOT reachable: {e}")
