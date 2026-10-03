# IdentityGuard

IdentityGuard is a Zero-Trust identity and access monitoring platform for detecting suspicious authentication and session activity.

## MVP pipeline

Authentication Event -> Normalizer -> Identity/Device Context -> Risk Detection -> Risk Score -> Security Alert -> Audit Log

## Detection rules

- Repeated failed authentication
- New or unrecognized device
- Impossible-travel pattern
- Privilege escalation
- Suspicious session activity

## Stack

- Python 3.11+
- FastAPI
- Pydantic
- pytest
- SQLite for the initial local MVP

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

> IdentityGuard is a defensive security research and monitoring project. It does not perform unauthorized access or exploitation.
