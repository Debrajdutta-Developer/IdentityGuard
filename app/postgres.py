import os
from typing import Any

import psycopg
from psycopg.rows import dict_row


SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    privilege TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    risk_level TEXT NOT NULL,
    reasons JSONB NOT NULL,
    previous_hash TEXT NOT NULL DEFAULT '',
    entry_hash TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (event_id, tenant_id)
);

CREATE TABLE IF NOT EXISTS security_alerts (
    id BIGSERIAL PRIMARY KEY,
    alert_id TEXT NOT NULL UNIQUE,
    tenant_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL,
    reasons JSONB NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant_created ON audit_events(tenant_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_alert_tenant_status ON security_alerts(tenant_id, status, id DESC);
"""


def database_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://"):]
    return url


def connect() -> psycopg.Connection[Any]:
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is required for PostgreSQL")
    return psycopg.connect(url, row_factory=dict_row)


def init_postgres() -> None:
    with connect() as connection:
        connection.execute(SCHEMA)
        connection.commit()
