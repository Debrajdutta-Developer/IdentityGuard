import hashlib
import hmac
import os
from datetime import datetime, timezone
from uuid import uuid4

from app.db import get_connection, init_db

API_KEYS = {
    key: role
    for key, role in (
        item.split(":", 1)
        for item in os.getenv("IDENTITYGUARD_API_KEYS", "dev-key:admin").split(",")
        if ":" in item
    )
}

ALLOWED_ROLES = {"admin", "analyst", "viewer"}


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def authenticate(api_key: str | None, tenant_id: str | None = None) -> str | None:
    if not api_key:
        return None

    for stored_key, role in API_KEYS.items():
        if hmac.compare_digest(_hash_key(api_key), _hash_key(stored_key)):
            return role if role in ALLOWED_ROLES else None

    init_db()
    key_hash = _hash_key(api_key)
    now = datetime.now(timezone.utc)
    with get_connection() as connection:
        row = connection.execute(
            "SELECT role, tenant_id, expires_at, revoked_at FROM api_keys WHERE key_hash = ?",
            (key_hash,),
        ).fetchone()

    if row is None or row["revoked_at"]:
        return None
    if tenant_id is not None and row["tenant_id"] != tenant_id:
        return None
    if row["role"] not in ALLOWED_ROLES:
        return None
    if row["expires_at"]:
        expires = datetime.fromisoformat(row["expires_at"])
        if expires <= now:
            return None
    return row["role"]


def create_api_key(tenant_id: str, role: str, expires_at: str | None = None) -> dict:
    if role not in ALLOWED_ROLES:
        raise ValueError("Invalid API key role")
    if not tenant_id or len(tenant_id) > 128:
        raise ValueError("Invalid tenant ID")

    init_db()
    secret = "ig_" + uuid4().hex + uuid4().hex
    key_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        connection.execute(
            """INSERT INTO api_keys
            (key_id,tenant_id,key_hash,role,expires_at,revoked_at,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (key_id, tenant_id, _hash_key(secret), role, expires_at, None, created_at),
        )
        connection.commit()
    return {"key_id": key_id, "api_key": secret, "tenant_id": tenant_id, "role": role, "expires_at": expires_at}


def revoke_api_key(key_id: str, tenant_id: str) -> bool:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE api_keys SET revoked_at = ? WHERE key_id = ? AND tenant_id = ? AND revoked_at IS NULL",
            (now, key_id, tenant_id),
        )
        connection.commit()
    return cursor.rowcount == 1
