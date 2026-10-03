import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db import get_connection, init_db


def record_assessment(event: dict, assessment: dict) -> dict:
    init_db()
    event_id = event.get("event_id") or str(uuid4())
    tenant_id = event.get("tenant_id", "default")
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT event_id, created_at FROM audit_events WHERE event_id = ? AND tenant_id = ?",
            (event_id, tenant_id),
        ).fetchone()
        if existing is not None:
            return {
                "event_id": existing["event_id"],
                "created_at": existing["created_at"],
                "idempotent": True,
            }

        connection.execute(
            """INSERT INTO audit_events
            (event_id,tenant_id,user_id,timestamp,action,outcome,privilege,risk_score,risk_level,reasons,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, tenant_id, event["user_id"], event["timestamp"], event["action"],
             event["outcome"], event["privilege"], assessment["risk_score"],
             assessment["risk_level"], json.dumps(assessment["reasons"]), created_at),
        )
        connection.commit()
    return {"event_id": event_id, "created_at": created_at, "idempotent": False}


def list_audit_events(limit: int = 50, tenant_id: str = "default") -> list[dict]:
    init_db()
    limit = max(1, min(limit, 100))
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT event_id,tenant_id,user_id,timestamp,action,outcome,privilege,
                      risk_score,risk_level,reasons,created_at
               FROM audit_events WHERE tenant_id = ? ORDER BY id DESC LIMIT ?""",
            (tenant_id, limit),
        ).fetchall()
    return [{**dict(row), "reasons": json.loads(row["reasons"])} for row in rows]
