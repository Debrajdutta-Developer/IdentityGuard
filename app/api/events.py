from fastapi import APIRouter, Depends, Header
from app.api.dependencies import require_api_key
from app.models.context import IdentityContext
from app.models.events import AuthEvent
from app.services.audit_ledger import record_assessment
from app.services.risk_engine import evaluate_event
from app.services.alert_service import create_alert

router = APIRouter(tags=["events"])

@router.post("/events/evaluate")
def evaluate_auth_event(event: AuthEvent, context: IdentityContext | None = None, role: str = Depends(require_api_key), x_tenant_id: str | None = Header(default=None)) -> dict:
    if x_tenant_id:
        event = event.model_copy(update={"tenant_id": x_tenant_id})
    event_data = event.model_dump(mode="json")
    assessment = evaluate_event(event, context)
    audit = record_assessment(event_data, assessment)
    alert = create_alert(event_data, assessment, audit)
    return {"event": event_data, "assessment": assessment, "decision": assessment["decision"], "audit": audit, "alert": alert, "role": role}
