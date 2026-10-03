import os
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "IdentityGuard")
    environment: str = os.getenv("ENVIRONMENT", "development")
    risk_threshold: int = int(os.getenv("RISK_THRESHOLD", "70"))
    allowed_hosts: list[str] = field(default_factory=lambda: [
        host.strip() for host in os.getenv(
            "ALLOWED_HOSTS", "127.0.0.1,localhost,*.localhost,testserver"
        ).split(",") if host.strip()
    ])

settings = Settings()
