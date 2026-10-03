from app.detection.rules import (
    detect_impossible_travel,
    detect_new_device,
    detect_privilege_escalation,
)
from app.models.context import IdentityContext
from app.models.events import AuthEvent


def evaluate_event(event: AuthEvent, context: IdentityContext | None = None) -> dict:
    context = context or IdentityContext()

    score = 0
    reasons: list[str] = []
    detections: list[dict] = []

    def apply(result) -> None:
        nonlocal score
        if result.triggered:
            score += result.score
            reasons.append(result.reason)
        detections.append({
            "rule": result.rule,
            "triggered": result.triggered,
            "score": result.score,
            "reason": result.reason,
        })

    if event.outcome == "failure":
        score += min(event.failed_attempts * 10, 40)
        if event.failed_attempts >= 5:
            reasons.append("repeated_failed_authentication")

    apply(detect_new_device(known_device=context.known_device))
    apply(detect_privilege_escalation(
        previous_privilege=context.previous_privilege,
        current_privilege=event.privilege,
    ))
    apply(detect_impossible_travel(
        distance_km=context.distance_km,
        elapsed_minutes=context.elapsed_minutes,
    ))

    level = "low"
    if score >= 70:
        level = "critical"
    elif score >= 40:
        level = "high"
    elif score >= 20:
        level = "medium"

    score = min(score, 100)
    decision = "deny" if level == "critical" else "step_up" if level == "high" else "allow"
    return {
        "risk_score": score,
        "risk_level": level,
        "decision": decision,
        "reasons": reasons,
        "detections": detections,
    }
