from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel

from app.api.dependencies import require_api_key, require_roles
from app.services.alert_service import add_alert_evidence, get_alert, get_alert_timeline, list_alerts, update_alert_status

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertStatusUpdate(BaseModel):
    status: Literal["open", "acknowledged", "resolved"]


@router.get("")
def get_alerts(
    limit: int = Query(default=50, ge=1, le=100),
    status: str | None = Query(default=None),
    role: str = Depends(require_api_key),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    return {"tenant_id": tenant_id, "alerts": list_alerts(limit, tenant_id, status), "role": role}


@router.get("/{alert_id}")
def get_single_alert(
    alert_id: str,
    role: str = Depends(require_api_key),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    alert = get_alert(alert_id, tenant_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": alert, "role": role}


@router.patch("/{alert_id}/status")
def set_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    role: str = Depends(require_roles("admin", "analyst")),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    alert = update_alert_status(alert_id, payload.status, tenant_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": alert, "role": role}


class AlertEvidence(BaseModel):
    evidence_type: str
    summary: str
    data: dict = {}


@router.get("/{alert_id}/timeline")
def alert_timeline(
    alert_id: str,
    role: str = Depends(require_api_key),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    if get_alert(alert_id, tenant_id) is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert_id": alert_id, "timeline": get_alert_timeline(alert_id, tenant_id), "role": role}


@router.post("/{alert_id}/evidence")
def add_evidence(
    alert_id: str,
    payload: AlertEvidence,
    role: str = Depends(require_roles("admin", "analyst")),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    evidence = add_alert_evidence(alert_id, payload.evidence_type, payload.summary, payload.data, tenant_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"evidence": evidence, "role": role}
