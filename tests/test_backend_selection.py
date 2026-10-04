from app import db_backend


def test_default_backend_is_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert db_backend.database_url() == "sqlite:///identityguard.db"
    assert db_backend.backend_name() == "sqlite"
    assert db_backend.is_postgres() is False


def test_postgres_backend_is_selected(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://identityguard:test@db.example/identityguard")
    assert db_backend.is_postgres() is True
    assert db_backend.backend_name() == "postgresql"
    assert db_backend.backend_status() == {"backend": "postgresql", "production_ready": True}


def test_postgres_scheme_variants_are_supported(monkeypatch):
    for url in (
        "postgres://identityguard:test@db.example/identityguard",
        "postgresql://identityguard:test@db.example/identityguard",
    ):
        monkeypatch.setenv("DATABASE_URL", url)
        assert db_backend.is_postgres() is True
