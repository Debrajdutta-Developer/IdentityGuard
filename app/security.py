import hashlib
import hmac
import os

API_KEYS = {
    key: role
    for key, role in (
        item.split(":", 1)
        for item in os.getenv("IDENTITYGUARD_API_KEYS", "dev-key:admin").split(",")
        if ":" in item
    )
}


def authenticate(api_key: str | None) -> str | None:
    if not api_key:
        return None
    for stored_key, role in API_KEYS.items():
        if hmac.compare_digest(
            hashlib.sha256(api_key.encode()).digest(),
            hashlib.sha256(stored_key.encode()).digest(),
        ):
            return role
    return None
