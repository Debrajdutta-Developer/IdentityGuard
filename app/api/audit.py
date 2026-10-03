from fastapi import APIRouter, Query
from app.services.audit_ledger import list_audit_events

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
def get_audit_events(limit: int = Query(default=50, ge=1, le=100)) -> dict:
    return {"events": list_audit_events(limit)}
