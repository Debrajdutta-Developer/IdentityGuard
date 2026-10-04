import os
import sqlite3
from pathlib import Path
from typing import Any

from app.db_backend import is_postgres

DB_PATH = Path("identityguard.db")


class _PostgresConnection:
    def __init__(self, connection: Any):
        self._connection = connection

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        return self._connection.__exit__(exc_type, exc, tb)

    def execute(self, query: str, params=()):
        # Keep the existing service SQL portable while PostgreSQL uses psycopg's
        # parameter syntax internally.
        return self._connection.execute(query.replace("?", "%s"), params)

    def __getattr__(self, name: str):
        return getattr(self._connection, name)


def get_connection():
    if is_postgres():
        from app.postgres import connect
        return _PostgresConnection(connect())

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    if is_postgres():
        from app.postgres import init_postgres
        init_postgres()
        return

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                tenant_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                outcome TEXT NOT NULL,
                privilege TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                reasons TEXT NOT NULL,
                previous_hash TEXT NOT NULL DEFAULT "",
                entry_hash TEXT NOT NULL DEFAULT "",
                created_at TEXT NOT NULL
            )
        """)
        columns = {row[1] for row in connection.execute("PRAGMA table_info(audit_events)").fetchall()}
        if "tenant_id" not in columns:
            connection.execute("ALTER TABLE audit_events ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default'")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL UNIQUE,
                tenant_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                title TEXT NOT NULL,
                reasons TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_audit_tenant_created ON audit_events(tenant_id, id DESC)")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS alert_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_id TEXT NOT NULL UNIQUE,
                tenant_id TEXT NOT NULL,
                alert_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                summary TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_alert_tenant_status ON security_alerts(tenant_id, status, id DESC)")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL UNIQUE,
                tenant_id TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_evidence_alert ON alert_evidence(tenant_id, alert_id, id ASC)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_tenant ON api_keys(tenant_id, revoked_at, expires_at)")
        connection.commit()
