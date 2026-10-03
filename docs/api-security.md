# API Security

IdentityGuard protects its API with an API key supplied through the `X-API-Key` header.

## Configuration

Set `IDENTITYGUARD_API_KEYS=admin-key:admin,viewer-key:viewer` in the environment. Never commit real API keys.

## Roles

- `admin`: administrative access
- `viewer`: read-only monitoring access

Production deployments should use TLS, key rotation, rate limiting, short-lived credentials, and a managed identity provider.
