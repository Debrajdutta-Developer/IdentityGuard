from collections.abc import Callable

from fastapi import Header, HTTPException

from app.security import authenticate


def require_api_key(
    x_api_key: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> str:
    role = authenticate(x_api_key, x_tenant_id)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return role


def require_roles(*allowed_roles: str) -> Callable[[str], str]:
    allowed = set(allowed_roles)

    def checker(role: str) -> str:
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return role

    return checker


def require_admin(role: str) -> str:
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return role
