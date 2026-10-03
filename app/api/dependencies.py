from fastapi import Header, HTTPException

from app.security import authenticate


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    role = authenticate(x_api_key)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return role


def require_admin(role: str) -> str:
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return role
