from fastapi import APIRouter, Depends, Header, Query
from app.api.dependencies import require_api_key
from app.services.audit_ledger import list_audit_events

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/events")
def get_audit_events(limit: int = Query(default=50, ge=1, le=100), role: str = Depends(require_api_key), x_tenant_id: str | None = Header(default=None)) -> dict:
    tenant_id = x_tenant_id or "default"
    return {"tenant_id": tenant_id, "events": list_audit_events(limit, tenant_id), "role": role}
