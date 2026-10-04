from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.audit import router as audit_router
from app.api.events import router as events_router
from app.api.identity import router as identity_router
from app.api.alerts import router as alerts_router
from app.api.api_keys import router as api_keys_router
from app.config import settings
from app.db import init_db
from app.models.context import IdentityContext
from app.models.events import AuthEvent
from app.services.audit_ledger import record_assessment
from app.services.risk_engine import evaluate_event
from app.middleware import RateLimitMiddleware

settings.validate()

app = FastAPI(
    title=settings.app_name,
    version="0.5.0",
    description="Zero-Trust identity and access monitoring platform.",
)

init_db()
app.add_middleware(RateLimitMiddleware, limit=60, window_seconds=60)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["X-API-Key", "X-Tenant-ID", "Content-Type"],
)

app.include_router(events_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(identity_router, prefix="/api/v1")
app.include_router(alerts_router, prefix="/api/v1")
app.include_router(api_keys_router, prefix="/api/v1")

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.get("/", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse("demo/index.html", media_type="text/html")

@app.post("/api/v1/demo/evaluate", include_in_schema=False)
def demo_evaluate(scenario: Literal["normal", "suspicious", "impossible_travel", "privilege_escalation"] = "suspicious") -> dict:
    """Run a synthetic scenario through the real IdentityGuard engine."""
    now = datetime.now(timezone.utc)
    if scenario == "normal":
        event = AuthEvent(user_id="demo_user", timestamp=now, ip_address="203.0.113.10", device_id="demo-known-device", action="login", outcome="success", privilege="user", failed_attempts=0, country="IN")
        context = IdentityContext(known_device=True, previous_privilege="user", distance_km=0, elapsed_minutes=30)
    elif scenario == "impossible_travel":
        event = AuthEvent(user_id="demo_user", timestamp=now, ip_address="203.0.113.11", device_id="demo-known-device", action="login", outcome="success", privilege="user", failed_attempts=0, country="IN")
        context = IdentityContext(known_device=True, previous_privilege="user", distance_km=850, elapsed_minutes=20)
    elif scenario == "privilege_escalation":
        event = AuthEvent(user_id="demo_admin", timestamp=now, ip_address="203.0.113.12", device_id="demo-known-device", action="login", outcome="success", privilege="admin", failed_attempts=0, country="IN")
        context = IdentityContext(known_device=True, previous_privilege="user", distance_km=0, elapsed_minutes=30)
    else:
        event = AuthEvent(user_id="demo_user", timestamp=now, ip_address="203.0.113.13", device_id="demo-new-device", action="login", outcome="failure", privilege="admin", failed_attempts=5, country="IN")
        context = IdentityContext(known_device=False, previous_privilege="user", distance_km=850, elapsed_minutes=20)
    event_data = event.model_dump(mode="json")
    assessment = evaluate_event(event, context)
    audit = record_assessment(event_data, assessment)
    from app.services.alert_service import create_alert
    alert = create_alert(event_data, assessment, audit)
    return {"event": event_data, "context": context.model_dump(), "assessment": assessment, "audit": audit, "alert": alert, "demo": True}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}

@app.get("/ready")
def readiness() -> dict[str, str]:
    try:
        init_db()
        return {"status": "ready", "service": settings.app_name}
    except Exception:
        return {"status": "not_ready", "service": settings.app_name}
