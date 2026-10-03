from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.dependencies import require_admin
from app.security import create_api_key, revoke_api_key

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


class CreateAPIKeyRequest(BaseModel):
    role: str = "viewer"
    expires_at: str | None = None


@router.post("")
def create_key(
    payload: CreateAPIKeyRequest,
    role: str = Depends(require_admin),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    try:
        result = create_api_key(tenant_id, payload.role, payload.expires_at)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"api_key": result, "role": role}


@router.delete("/{key_id}")
def revoke_key(
    key_id: str,
    role: str = Depends(require_admin),
    x_tenant_id: str | None = Header(default=None),
) -> dict:
    tenant_id = x_tenant_id or "default"
    if not revoke_api_key(key_id, tenant_id):
        raise HTTPException(status_code=404, detail="API key not found or already revoked")
    return {"key_id": key_id, "revoked": True, "role": role}
