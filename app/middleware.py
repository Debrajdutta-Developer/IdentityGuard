import os
import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_REQUESTS: dict[str, list[float]] = defaultdict(list)
_LOCK = Lock()
_REDIS = None


async def _redis_client():
    global _REDIS
    url = os.getenv("REDIS_URL")
    if not url:
        return None
    if _REDIS is None:
        from redis.asyncio import Redis
        _REDIS = Redis.from_url(url, decode_responses=True)
    try:
        await _REDIS.ping()
    except Exception:
        return None
    return _REDIS


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request, call_next):
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        redis = await _redis_client()

        if redis is not None:
            bucket = int(time.time() // self.window_seconds)
            key = f"identityguard:ratelimit:{client}:{bucket}"
            try:
                count = await redis.incr(key)
                if count == 1:
                    await redis.expire(key, self.window_seconds + 1)
                if count > self.limit:
                    return JSONResponse(
                        {"detail": "Rate limit exceeded"},
                        status_code=429,
                        headers={"Retry-After": str(self.window_seconds)},
                    )
            except Exception:
                # Redis is an enhancement, not a single point of failure.
                redis = None

        if redis is None:
            now = time.monotonic()
            with _LOCK:
                recent = [t for t in _REQUESTS[client] if now - t < self.window_seconds]
                if len(recent) >= self.limit:
                    _REQUESTS[client] = recent
                    return JSONResponse(
                        {"detail": "Rate limit exceeded"},
                        status_code=429,
                        headers={"Retry-After": str(self.window_seconds)},
                    )
                recent.append(now)
                _REQUESTS[client] = recent

        return await call_next(request)
