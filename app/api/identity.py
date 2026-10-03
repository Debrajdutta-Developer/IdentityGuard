from fastapi import APIRouter
from app.identity import get_workload_identity
from app.spire_client import SpireUnavailable, fetch_spiffe_identity

router = APIRouter(prefix="/identity", tags=["identity"])

@router.get("/workload")
def workload_identity() -> dict:
    try:
        identity = fetch_spiffe_identity()
        return {"status": "available", "identity": identity.spiffe_id, "source": identity.source}
    except SpireUnavailable:
        identity = get_workload_identity()
        if identity is None:
            return {"status": "unavailable", "identity": None}
        return {"status": "configured", "identity": identity.spiffe_id, "source": identity.source}
