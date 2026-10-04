from fastapi.testclient import TestClient

from app.db import DB_PATH
from app.main import app
from app.security import authenticate, create_api_key, revoke_api_key


def test_database_api_key_is_tenant_bound(tmp_path, monkeypatch):
    db_path = tmp_path / "rbac.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)

    key = create_api_key("tenant-a", "analyst")

    assert authenticate(key["api_key"], "tenant-a") == "analyst"
    assert authenticate(key["api_key"], "tenant-b") is None


def test_revoked_api_key_cannot_authenticate(tmp_path, monkeypatch):
    db_path = tmp_path / "revoke.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)

    key = create_api_key("tenant-a", "analyst")
    assert revoke_api_key(key["key_id"], "tenant-a") is True
    assert authenticate(key["api_key"], "tenant-a") is None


def test_viewer_cannot_mutate_alerts(tmp_path, monkeypatch):
    db_path = tmp_path / "api.db"
    monkeypatch.setattr("app.db.DB_PATH", db_path)

    key = create_api_key("tenant-a", "viewer")
    client = TestClient(app)

    response = client.patch(
        "/alerts/nonexistent/status",
        headers={"X-API-Key": key["api_key"], "X-Tenant-ID": "tenant-a"},
        json={"status": "resolved"},
    )

    assert response.status_code == 403
