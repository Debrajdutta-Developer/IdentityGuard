import ssl
from pathlib import Path
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class MTLSConfigurationError(RuntimeError):
    pass

def build_server_context(cert_file: str, key_file: str, trust_bundle: str) -> ssl.SSLContext:
    for value in (cert_file, key_file, trust_bundle):
        if not Path(value).is_file():
            raise MTLSConfigurationError(f"mTLS file not found: {value}")
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    context.load_verify_locations(cafile=trust_bundle)
    return context

class SpiffeMTLSGuard(BaseHTTPMiddleware):
    def __init__(self, app, allowed_spiffe_ids: set[str], trusted_header: str = "x-spiffe-id"):
        super().__init__(app)
        self.allowed_spiffe_ids = allowed_spiffe_ids
        self.trusted_header = trusted_header

    async def dispatch(self, request: Request, call_next: Callable):
        identity = request.headers.get(self.trusted_header)
        if identity not in self.allowed_spiffe_ids:
            return JSONResponse({"detail": "mTLS workload identity required"}, status_code=403)
        return await call_next(request)
