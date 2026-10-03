from fastapi import FastAPI

from app.api.events import router as events_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Zero-Trust identity and access monitoring platform.",
)

app.include_router(events_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
