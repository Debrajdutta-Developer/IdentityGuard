from pydantic import BaseModel, Field


class IdentityContext(BaseModel):
    known_device: bool = True
    previous_privilege: str = Field(default="user", pattern="^(user|admin)$")
    distance_km: float = Field(default=0, ge=0)
    elapsed_minutes: float = Field(default=0, ge=0)
