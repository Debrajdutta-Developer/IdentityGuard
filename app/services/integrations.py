import json
import os
import urllib.request


def emit_webhook(event: dict) -> bool:
    """Best-effort outbound security event webhook.

    Disabled unless SECURITY_WEBHOOK_URL is configured. Failures are isolated
    from the authentication request path and are reported as False.
    """
    url = os.getenv("SECURITY_WEBHOOK_URL")
    if not url:
        return False
    payload = json.dumps(event).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "IdentityGuard/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return 200 <= response.status < 300
    except Exception:
        return False
