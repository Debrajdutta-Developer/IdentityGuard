import asyncio

from app import middleware


class FakeRedis:
    def __init__(self):
        self.counts = {}
        self.expirations = {}

    async def incr(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key, seconds):
        self.expirations[key] = seconds
        return True


class FakeClient:
    host = "10.0.0.10"


class FakeRequest:
    def __init__(self, path="/api/v1/events"):
        self.url = type("URL", (), {"path": path})()
        self.client = FakeClient()


async def _resolved(value):
    return value


async def _response_handler(request):
    from starlette.responses import Response
    return Response(status_code=200)


def test_redis_rate_limiter_returns_429_after_limit(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(middleware, "_redis_client", lambda: _resolved(redis))
    limiter = middleware.RateLimitMiddleware(lambda request: None, limit=2, window_seconds=60)

    first, second, third = asyncio.run(_run_three(limiter))

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert redis.expirations


async def _run_three(limiter):
    request = FakeRequest()
    return (
        await limiter.dispatch(request, _response_handler),
        await limiter.dispatch(request, _response_handler),
        await limiter.dispatch(request, _response_handler),
    )


def test_redis_failure_falls_back_to_local_limiter(monkeypatch):
    class BrokenRedis:
        async def incr(self, key):
            raise RuntimeError("redis unavailable")

    monkeypatch.setattr(middleware, "_redis_client", lambda: _resolved(BrokenRedis()))
    middleware._REQUESTS.clear()
    limiter = middleware.RateLimitMiddleware(lambda request: None, limit=1, window_seconds=60)

    async def run():
        request = FakeRequest("/api/v1/a")
        return (
            await limiter.dispatch(request, _response_handler),
            await limiter.dispatch(request, _response_handler),
        )

    first, second = asyncio.run(run())
    assert first.status_code == 200
    assert second.status_code == 429
