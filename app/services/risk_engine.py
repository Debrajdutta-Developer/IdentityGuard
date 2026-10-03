from app.models.events import AuthEvent


def evaluate_event(event: AuthEvent) -> dict:
    score = 0
    reasons: list[str] = []

    if event.outcome == "failure":
        score += min(event.failed_attempts * 10, 40)
        if event.failed_attempts >= 5:
            reasons.append("repeated_failed_authentication")

    if event.privilege == "admin" and event.action == "login":
        score += 10
        reasons.append("privileged_login")

    if event.action == "password_change" and event.outcome == "success":
        score += 5
        reasons.append("credential_change")

    level = "low"
    if score >= 70:
        level = "critical"
    elif score >= 40:
        level = "high"
    elif score >= 20:
        level = "medium"

    return {
        "risk_score": min(score, 100),
        "risk_level": level,
        "reasons": reasons,
    }
