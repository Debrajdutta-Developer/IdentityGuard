from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_audit_requires_api_key():
    assert client.get('/api/v1/audit/events').status_code == 401

def test_audit_accepts_valid_api_key():
    import app.security as security
    security.API_KEYS = {'test-key': 'viewer'}
    response = client.get('/api/v1/audit/events', headers={'X-API-Key': 'test-key'})
    assert response.status_code == 200
