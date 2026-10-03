from dataclasses import dataclass
import os

@dataclass(frozen=True)
class WorkloadIdentity:
    spiffe_id: str
    source: str = "static"

def get_workload_identity() -> WorkloadIdentity | None:
    spiffe_id = os.getenv("SPIFFE_ID")
    if not spiffe_id:
        return None
    if not spiffe_id.startswith("spiffe://"):
        raise ValueError("SPIFFE_ID must use the spiffe:// URI scheme")
    return WorkloadIdentity(spiffe_id=spiffe_id)
