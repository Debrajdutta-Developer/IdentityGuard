# IdentityGuard Security Controls

## Implemented

- API key authentication
- Viewer/admin role model
- In-memory request rate limiting
- Trusted host validation
- Restricted CORS configuration
- Security response headers
- Persistent audit ledger

## Rate limiting

The current MVP allows 60 requests per client per 60-second window. The health endpoint is excluded.

This limiter is intentionally simple and process-local. A production multi-instance deployment should use a shared store such as Redis and centralized rate-limit policy.

## Production hardening

Use HTTPS/TLS, secret rotation, a managed identity provider, centralized rate limiting, structured security logging, and restrictive deployment configuration.
