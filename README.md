# IdentityGuard

IdentityGuard is a Zero-Trust identity and access monitoring platform for detecting suspicious authentication and session activity.

## Architecture

Authentication Event -> Identity/Device Context -> Detection Rules -> Risk Score -> Security Alert -> Audit Ledger

Identity layer:

SPIRE Agent -> Workload API -> X.509-SVID -> SPIFFE identity -> mTLS trust boundary

## Detection rules

- Repeated failed authentication
- New or unrecognized device
- Impossible-travel pattern
- Privilege escalation
- Suspicious session activity

## Security controls

- API-key authentication with viewer/admin roles
- Persistent SQLite audit ledger
- Request rate limiting
- Trusted-host validation
- Restricted CORS
- Security response headers
- Optional SPIFFE/SPIRE workload identity
- TLS 1.3 mTLS verification boundary

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- pytest
- SQLite for the initial local MVP
- cryptography for X.509 certificate parsing

## Quick start

Create a virtual environment, install requirements, then run:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

API docs: http://127.0.0.1:8000/docs

## API authentication

Protected endpoints require the X-API-Key header.

Example:
curl -H "X-API-Key: dev-key" http://127.0.0.1:8000/api/v1/audit/events

Never use the example key outside local development.

## SPIFFE/SPIRE

Set SPIFFE_ENDPOINT_SOCKET to the local SPIRE Agent Workload API socket. IdentityGuard attempts to obtain an X.509-SVID and exposes only its SPIFFE ID through /api/v1/identity/workload.

If SPIRE is unavailable, the optional SPIFFE_ID environment variable is treated only as development configuration, not cryptographic authentication.

> IdentityGuard is a defensive security research and monitoring project. It does not perform unauthorized access or exploitation.
