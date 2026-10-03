import sqlite3
from pathlib import Path

DB_PATH = Path("identityguard.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
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
