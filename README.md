# IdentityGuard

**Enterprise Identity Threat Detection & Response Platform**

IdentityGuard is a defensive identity-security platform for ingesting authentication telemetry, correlating identity context, detecting risky access patterns, making policy decisions, and preserving tenant-scoped audit evidence.

## Production architecture

```text
Authentication Event
        |
        v
Tenant + Identity Context
        |
        v
Detection + Risk Engine
        |
        v
Policy Decision: allow / step-up / deny
        |
        +----> Security Alert
        |
        v
Tenant-scoped Audit Ledger

Production infrastructure:
PostgreSQL -> durable application data
Redis      -> distributed rate limiting
FastAPI    -> API + policy boundary
SPIRE      -> workload identity / X.509-SVID
``` 

## Detection capabilities

- Repeated failed authentication
- New or unrecognized device
- Impossible-travel patterns
- Privilege escalation
- Suspicious session activity

## Security controls

- API-key authentication with role-based authorization
- Tenant-scoped event, alert, and audit boundaries
- Explicit access decision output: allow / step-up / deny
- Persistent audit ledger
- Redis-backed distributed rate limiting with safe local fallback
- PostgreSQL production backend support
- Trusted-host validation
- Environment-aware production configuration validation
- Restricted CORS
- Security response headers and HSTS in production
- Optional SPIFFE/SPIRE workload identity
- X.509 certificate parsing
- TLS 1.3 mTLS verification boundary
- Automated CI security and integration testing

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness check |
| `GET /ready` | Application readiness check |
| `POST /api/v1/events/evaluate` | Evaluate an event and return a policy decision |
| `GET /api/v1/audit/events` | Read the audit ledger |
| `GET /api/v1/identity/workload` | Report workload identity status |

Protected endpoints require the `X-API-Key` header. Enterprise integrations can send `X-Tenant-ID` to isolate customer/organization telemetry.

## Production configuration

Set these environment variables in the deployment platform:

```text
ENVIRONMENT=production
ALLOWED_HOSTS=<your-production-hosts>
CORS_ORIGINS=<your-approved-origins>
DATABASE_URL=<managed-postgresql-url>
REDIS_URL=<managed-redis-url>
```

Do not commit credentials, API keys, database URLs, or Redis URLs to the repository.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API documentation at:

`http://127.0.0.1:8000/docs`

Run tests:

```bash
pytest -q
```

## SPIFFE/SPIRE

Set `SPIFFE_ENDPOINT_SOCKET` to the local SPIRE Agent Workload API socket. IdentityGuard attempts to obtain an X.509-SVID and exposes only its SPIFFE ID through the workload identity endpoint.

A manually configured `SPIFFE_ID` is only a development fallback and is **not** cryptographic proof of workload identity.

See:
- `docs/spiffe-spire.md`
- `docs/mtls.md`
- `docs/security-controls.md`
- `docs/api-security.md`

## Security scope

IdentityGuard is intended for **authorized defensive security monitoring and research**. It does not provide unauthorized access or exploitation functionality.

## Product direction

IdentityGuard is being developed toward a B2B deployment model: tenant isolation, policy decisions, identity/workload context, auditable security evidence, and integration-ready APIs. Production deployments should use managed infrastructure for the database, secrets, distributed rate limiting, observability, and high availability.


## Demo & presentation

### 🎥 Demo website video

[Watch the IdentityGuard demo video on Google Drive](https://drive.google.com/file/d/1l2BZVf-hckZ-asqZmkSYa4SMfrEkUpFi/view?usp=drivesdk)

### 📊 Project presentation

[View the IdentityGuard project PPT on Google Drive](https://drive.google.com/file/d/1hivxB-hCFPiW3rz5w0FaCG0hMrn_BmHD/view?usp=drivesdk)


## Author

**Debraj Dutta — The Ghost**

Cybersecurity • Zero-Trust • Identity Security • Security Automation
