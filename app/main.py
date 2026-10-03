from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.audit import router as audit_router
from app.api.events import router as events_router
from app.api.identity import router as identity_router
from app.config import settings
from app.db import init_db
from app.middleware import RateLimitMiddleware

app = FastAPI(
    title=settings.app_name,
    version="0.4.0",
    description="Zero-Trust identity and access monitoring platform.",
)

init_db()

app.add_middleware(RateLimitMiddleware, limit=60, window_seconds=60)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "*.localhost"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

app.include_router(events_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(identity_router, prefix="/api/v1")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
