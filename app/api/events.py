from fastapi import APIRouter

from app.models.events import AuthEvent
from app.services.risk_engine import evaluate_event

router = APIRouter(tags=["events"])


@router.post("/events/evaluate")
def evaluate_auth_event(event: AuthEvent) -> dict:
    assessment = evaluate_event(event)
    return {
        "event": event.model_dump(),
        "assessment": assessment,
    }
