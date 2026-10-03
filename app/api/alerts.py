from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Literal

from app.api.dependencies import require_api_key
from app.services.alert_service import get_alert, list_alerts, update_alert_status

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
    role: str = Depends(require_api_key),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    alert = update_alert_status(alert_id, payload.status, tenant_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": alert, "role": role}
