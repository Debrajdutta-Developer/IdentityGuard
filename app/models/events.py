from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Literal

from pydantic import BaseModel, Field


class AuthEvent(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    timestamp: datetime
    ip_address: IPv4Address | IPv6Address
    device_id: str = Field(min_length=1, max_length=128)
    action: Literal["login", "logout", "token_refresh", "password_change"]
    outcome: Literal["success", "failure"]
    privilege: Literal["user", "admin"] = "user"
    failed_attempts: int = Field(default=0, ge=0)
    country: str | None = Field(default=None, max_length=64)
