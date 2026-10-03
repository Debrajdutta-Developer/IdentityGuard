import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "IdentityGuard")
    environment: str = os.getenv("ENVIRONMENT", "development")
    risk_threshold: int = int(os.getenv("RISK_THRESHOLD", "70"))


settings = Settings()
