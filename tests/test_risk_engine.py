from datetime import datetime, timezone

from app.models.events import AuthEvent
from app.services.risk_engine import evaluate_event


def test_repeated_failures_raise_high_risk() -> None:
    event = AuthEvent(
        user_id="user-001",
        timestamp=datetime.now(timezone.utc),
        ip_address="192.0.2.10",
        device_id="device-001",
        action="login",
        outcome="failure",
        failed_attempts=5,
    )

    result = evaluate_event(event)

    assert result["risk_score"] >= 40
    assert "repeated_failed_authentication" in result["reasons"]
