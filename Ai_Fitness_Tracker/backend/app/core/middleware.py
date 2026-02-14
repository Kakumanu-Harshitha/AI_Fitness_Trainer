import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from .redis import RedisService
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """
    ASGI Middleware for rate limiting that safely handles both HTTP and WebSockets.
    Avoids BaseHTTPMiddleware which is known to break WebSocket handshakes.
    """
    def __init__(self, app, redis_service: RedisService, limit: int = 60, window: int = 60):
        self.app = app
        self.redis = redis_service
        self.limit = limit
        self.window = window

    async def __call__(self, scope, receive, send):
        # Only apply rate limiting to HTTP requests
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Create a Request object from the scope
        request = Request(scope)

        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await self.app(scope, receive, send)

        # Skip rate limiting for non-API routes
        if not request.url.path.startswith("/api/v1"):
            return await self.app(scope, receive, send)

        try:
            client_ip = request.client.host if request.client else "unknown"
        except Exception:
            client_ip = "unknown"
            
        key = f"ratelimit:{client_ip}:{request.url.path}"
        
        try:
            current_count = await self.redis.get(key)
            if current_count is None:
                await self.redis.set(key, 1, expire=self.window)
            elif int(current_count) >= self.limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Too many requests. Please try again later."}
                )
                return await response(scope, receive, send)
            else:
                await self.redis.incr(key)
        except Exception as e:
            # Fallback: if Redis is down, allow the request but log the error
            logger.error(f"Rate limit error: {e}")
            pass

        return await self.app(scope, receive, send)
