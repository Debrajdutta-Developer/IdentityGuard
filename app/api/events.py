from fastapi import APIRouter

from app.models.context import IdentityContext
from app.models.events import AuthEvent
from app.services.risk_engine import evaluate_event

router = APIRouter(tags=["events"])


@router.post("/events/evaluate")
def evaluate_auth_event(event: AuthEvent, context: IdentityContext | None = None) -> dict:
    return {
        "event": event.model_dump(mode="json"),
        "assessment": evaluate_event(event, context),
    }
