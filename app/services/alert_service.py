import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db import get_connection, init_db


def create_alert(event: dict, assessment: dict, audit: dict) -> dict | None:
    if assessment["risk_level"] not in {"high", "critical"}:
        return None
    now = datetime.now(timezone.utc).isoformat()
    alert_id = str(uuid4())
    with get_connection() as connection:
        connection.execute(
            """INSERT INTO security_alerts
            (alert_id,tenant_id,event_id,user_id,severity,status,title,reasons,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                alert_id, event.get("tenant_id", "default"), audit["event_id"],
                event["user_id"], assessment["risk_level"], "open",
                "Suspicious identity activity detected",
                json.dumps(assessment["reasons"]), now, now,
            ),
        )
        connection.commit()
    return get_alert(alert_id, event.get("tenant_id", "default"))


def get_alert(alert_id: str, tenant_id: str = "default") -> dict | None:
    init_db()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM security_alerts WHERE alert_id = ? AND tenant_id = ?",
            (alert_id, tenant_id),
        ).fetchone()
    if row is None:
        return None
    result = dict(row)
    result["reasons"] = json.loads(result["reasons"])
    return result


def list_alerts(limit: int = 50, tenant_id: str = "default", status: str | None = None) -> list[dict]:
    init_db()
    limit = max(1, min(limit, 100))
    query = "SELECT * FROM security_alerts WHERE tenant_id = ?"
    params: list[object] = [tenant_id]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
    return [{**dict(row), "reasons": json.loads(row["reasons"])} for row in rows]


def update_alert_status(alert_id: str, status: str, tenant_id: str = "default") -> dict | None:
    if status not in {"open", "acknowledged", "resolved"}:
        raise ValueError("Invalid alert status")
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        connection.execute(
            "UPDATE security_alerts SET status = ?, updated_at = ? WHERE alert_id = ? AND tenant_id = ?",
            (status, now, alert_id, tenant_id),
        )
        connection.commit()
    return get_alert(alert_id, tenant_id)
