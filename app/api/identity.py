from fastapi import APIRouter
from app.identity import get_workload_identity

router = APIRouter(prefix="/identity", tags=["identity"])

@router.get("/workload")
def workload_identity() -> dict:
    identity = get_workload_identity()
    if identity is None:
        return {"status": "unavailable", "identity": None}
    return {"status": "available", "identity": identity.spiffe_id, "source": identity.source}
