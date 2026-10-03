def test_authenticate_valid_key(monkeypatch):
    monkeypatch.setenv("IDENTITYGUARD_API_KEYS", "test-key:admin")
    import app.security as security
    security.API_KEYS = {"test-key": "admin"}
    assert security.authenticate("test-key") == "admin"


def test_authenticate_invalid_key(monkeypatch):
    import app.security as security
    security.API_KEYS = {"test-key": "admin"}
    assert security.authenticate("wrong-key") is None
