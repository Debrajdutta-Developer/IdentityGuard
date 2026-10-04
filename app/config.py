import os
from dataclasses import dataclass, field


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "IdentityGuard")
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    risk_threshold: int = int(os.getenv("RISK_THRESHOLD", "70"))
    allowed_hosts: list[str] = field(default_factory=lambda: _csv_env(
        "ALLOWED_HOSTS", "127.0.0.1,localhost,*.localhost,testserver"
    ))
    cors_origins: list[str] = field(default_factory=lambda: _csv_env("CORS_ORIGINS", ""))

    def validate(self) -> None:
        if self.environment == "production":
            if not self.allowed_hosts:
                raise RuntimeError("ALLOWED_HOSTS must be configured in production")
            if "*" in self.allowed_hosts or "*.localhost" in self.allowed_hosts:
                raise RuntimeError("Wildcard/local ALLOWED_HOSTS are not permitted in production")


settings = Settings()
