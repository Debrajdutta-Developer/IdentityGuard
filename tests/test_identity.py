def test_workload_identity_from_spiffe_id(monkeypatch):
    monkeypatch.setenv("SPIFFE_ID", "spiffe://identityguard.example/api")
    from app.identity import get_workload_identity
    identity = get_workload_identity()
    assert identity is not None
    assert identity.spiffe_id == "spiffe://identityguard.example/api"

def test_workload_identity_unavailable(monkeypatch):
    monkeypatch.delenv("SPIFFE_ID", raising=False)
    from app.identity import get_workload_identity
    assert get_workload_identity() is None
