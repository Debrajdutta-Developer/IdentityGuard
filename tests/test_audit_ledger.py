def test_audit_ledger_round_trip(tmp_path, monkeypatch):
    import app.db as db
    from app.services.audit_ledger import list_audit_events, record_assessment

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    event = {
        "user_id": "user-test",
        "timestamp": "2026-10-03T10:00:00+00:00",
        "action": "login",
        "outcome": "success",
        "privilege": "user",
    }
    assessment = {
        "risk_score": 25,
        "risk_level": "medium",
        "reasons": ["device_not_seen_before"],
    }

    audit = record_assessment(event, assessment)
    events = list_audit_events()

    assert audit["event_id"]
    assert len(events) == 1
    assert events[0]["event_id"] == audit["event_id"]
