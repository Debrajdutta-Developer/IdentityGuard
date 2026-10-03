from fastapi import FastAPI

from app.api.audit import router as audit_router
from app.api.events import router as events_router
from app.config import settings
from app.db import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Zero-Trust identity and access monitoring platform.",
)

init_db()

app.include_router(events_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
