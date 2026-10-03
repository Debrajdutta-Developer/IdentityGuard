from app.detection.rules import (
    detect_impossible_travel,
    detect_new_device,
    detect_privilege_escalation,
)


def test_new_device_triggers() -> None:
    result = detect_new_device(known_device=False)
    assert result.triggered is True
    assert result.score == 25


def test_privilege_escalation_triggers() -> None:
    result = detect_privilege_escalation(previous_privilege="user", current_privilege="admin")
    assert result.triggered is True
    assert result.score == 35


def test_impossible_travel_triggers() -> None:
    result = detect_impossible_travel(distance_km=5000, elapsed_minutes=60)
    assert result.triggered is True
