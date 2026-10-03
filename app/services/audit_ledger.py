import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db import get_connection, init_db


def record_assessment(event: dict, assessment: dict) -> dict:
    init_db()
    event_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """INSERT INTO audit_events
            (event_id,tenant_id,user_id,timestamp,action,outcome,privilege,risk_score,risk_level,reasons,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, event.get("tenant_id", "default"), event["user_id"], event["timestamp"], event["action"],
             event["outcome"], event["privilege"], assessment["risk_score"],
             assessment["risk_level"], json.dumps(assessment["reasons"]), created_at),
        )
        connection.commit()
    return {"event_id": event_id, "created_at": created_at}


def list_audit_events(limit: int = 50, tenant_id: str = "default") -> list[dict]:
    init_db()
    limit = max(1, min(limit, 100))
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT event_id,tenant_id,user_id,timestamp,action,outcome,privilege,
                      risk_score,risk_level,reasons,created_at
               FROM audit_events ORDER BY id DESC LIMIT ?""", (limit,)
        ).fetchall()
    return [{**dict(row), "reasons": json.loads(row["reasons"])} for row in rows]
