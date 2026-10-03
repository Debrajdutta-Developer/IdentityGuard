# IdentityGuard

**Enterprise Identity Threat Detection & Response Platform**

IdentityGuard is a defensive identity-security platform for ingesting authentication telemetry, correlating identity context, detecting risky access patterns, making policy decisions, and preserving tenant-scoped audit evidence.

## Architecture

```
Authentication Event
        |
        v
Tenant + Identity Context
        |
        v
Detection Engine
        |
        v
Risk Engine
        |
        v
Policy Decision (allow / step-up / deny)
        |
        +----> Security Alert
        |
        v
Tenant-scoped Audit Ledger

Workload Identity:
SPIRE Agent -> Workload API -> X.509-SVID -> SPIFFE ID -> mTLS boundary
```

## Detection capabilities

- Repeated failed authentication
- New or unrecognized device
- Impossible-travel patterns
- Privilege escalation
- Suspicious session activity

## Security controls

- API-key authentication with viewer/admin roles
- Tenant-scoped event and audit boundaries
- Explicit access decision output (allow / step-up / deny)
- Persistent audit ledger
- Request rate limiting
- Trusted-host validation
- Restricted CORS
- Security response headers
- Optional SPIFFE/SPIRE workload identity
- X.509 certificate parsing
- TLS 1.3 mTLS verification boundary
- Automated CI testing

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Service health |
| `POST /api/v1/events/evaluate` | Evaluate an event and return a policy decision |
| `GET /api/v1/audit/events` | Read the audit ledger |
| `GET /api/v1/identity/workload` | Report workload identity status |

Protected endpoints require the `X-API-Key` header. Enterprise integrations can send `X-Tenant-ID` to isolate customer/organization telemetry.

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

IdentityGuard is being developed toward a B2B deployment model: tenant isolation, policy decisions, identity/workload context, auditable security evidence, and integration-ready APIs. The current repository remains an MVP foundation; production deployments should use managed infrastructure for the database, secrets, distributed rate limiting, observability, and high availability.

The project is designed so production deployments can later replace the local SQLite ledger, process-local rate limiter, and development credentials with managed infrastructure.

## Author

**Debraj Dutta — The Ghost**

Cybersecurity • Zero-Trust • Identity Security • Security Automation
