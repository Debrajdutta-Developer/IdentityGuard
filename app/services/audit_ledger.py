import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from app.db import get_connection, init_db


def _entry_hash(payload: dict, previous_hash: str) -> str:
    material = json.dumps(
        {"previous_hash": previous_hash, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(material).hexdigest()


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
            return {"event_id": existing["event_id"], "created_at": existing["created_at"], "idempotent": True}

        previous = connection.execute(
            "SELECT entry_hash FROM audit_events WHERE tenant_id = ? ORDER BY id DESC LIMIT 1",
            (tenant_id,),
        ).fetchone()
        previous_hash = previous["entry_hash"] if previous and previous["entry_hash"] else ""
        payload = {
            "event_id": event_id,
            "tenant_id": tenant_id,
            "user_id": event["user_id"],
            "timestamp": event["timestamp"],
            "action": event["action"],
            "outcome": event["outcome"],
            "privilege": event["privilege"],
            "risk_score": assessment["risk_score"],
            "risk_level": assessment["risk_level"],
            "reasons": assessment["reasons"],
            "created_at": created_at,
        }
        entry_hash = _entry_hash(payload, previous_hash)

        connection.execute(
            """INSERT INTO audit_events
            (event_id,tenant_id,user_id,timestamp,action,outcome,privilege,risk_score,risk_level,reasons,previous_hash,entry_hash,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (event_id, tenant_id, event["user_id"], event["timestamp"], event["action"],
             event["outcome"], event["privilege"], assessment["risk_score"],
             assessment["risk_level"], json.dumps(assessment["reasons"]),
             previous_hash, entry_hash, created_at),
        )
        connection.commit()
    return {"event_id": event_id, "created_at": created_at, "entry_hash": entry_hash, "idempotent": False}


def list_audit_events(limit: int = 50, tenant_id: str = "default") -> list[dict]:
    init_db()
    limit = max(1, min(limit, 100))
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT event_id,tenant_id,user_id,timestamp,action,outcome,privilege,
                      risk_score,risk_level,reasons,previous_hash,entry_hash,created_at
               FROM audit_events WHERE tenant_id = ? ORDER BY id DESC LIMIT ?""",
            (tenant_id, limit),
        ).fetchall()
    return [{**dict(row), "reasons": json.loads(row["reasons"])} for row in rows]


def verify_audit_chain(tenant_id: str = "default") -> dict:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT event_id,tenant_id,user_id,timestamp,action,outcome,privilege,
                      risk_score,risk_level,reasons,previous_hash,entry_hash,created_at
               FROM audit_events WHERE tenant_id = ? ORDER BY id ASC""",
            (tenant_id,),
        ).fetchall()

    previous_hash = ""
    for index, row in enumerate(rows, start=1):
        payload = {
            "event_id": row["event_id"],
            "tenant_id": row["tenant_id"],
            "user_id": row["user_id"],
            "timestamp": row["timestamp"],
            "action": row["action"],
            "outcome": row["outcome"],
            "privilege": row["privilege"],
            "risk_score": row["risk_score"],
            "risk_level": row["risk_level"],
            "reasons": json.loads(row["reasons"]),
            "created_at": row["created_at"],
        }
        expected = _entry_hash(payload, previous_hash)
        if row["previous_hash"] != previous_hash or row["entry_hash"] != expected:
            return {"valid": False, "checked_entries": index, "failed_event_id": row["event_id"]}
        previous_hash = row["entry_hash"]

    return {"valid": True, "checked_entries": len(rows), "tenant_id": tenant_id}
