from dataclasses import dataclass
from math import radians, sin, cos, asin, sqrt


@dataclass(frozen=True)
class DetectionResult:
    rule: str
    triggered: bool
    score: int
    reason: str


def detect_new_device(*, known_device: bool) -> DetectionResult:
    return DetectionResult(
        "new_device",
        not known_device,
        25 if not known_device else 0,
        "device_not_seen_before" if not known_device else "",
    )


def detect_privilege_escalation(*, previous_privilege: str, current_privilege: str) -> DetectionResult:
    triggered = previous_privilege != "admin" and current_privilege == "admin"
    return DetectionResult(
        "privilege_escalation",
        triggered,
        35 if triggered else 0,
        "privilege_changed_to_admin" if triggered else "",
    )


def detect_impossible_travel(
    *,
    distance_km: float,
    elapsed_minutes: float,
    max_speed_kmh: float = 900.0,
) -> DetectionResult:
    elapsed_hours = elapsed_minutes / 60
    impossible = elapsed_hours > 0 and distance_km / elapsed_hours > max_speed_kmh
    return DetectionResult(
        "impossible_travel",
        impossible,
        45 if impossible else 0,
        "travel_speed_exceeds_threshold" if impossible else "",
    )


def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    radius_km = 6371.0088
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * radius_km * asin(sqrt(a))
