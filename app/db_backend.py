import os
from typing import Any


def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///identityguard.db")


def is_postgres() -> bool:
    return database_url().startswith(("postgres://", "postgresql://"))


def backend_name() -> str:
    return "postgresql" if is_postgres() else "sqlite"


def backend_status() -> dict[str, Any]:
    return {"backend": backend_name(), "production_ready": is_postgres()}
