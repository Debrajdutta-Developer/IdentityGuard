import time
from collections import defaultdict
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

_REQUESTS: dict[str, list[float]] = defaultdict(list)
_LOCK = Lock()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
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
