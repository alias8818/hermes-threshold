from __future__ import annotations

from fastapi.testclient import TestClient

from hermes_threshold.app import create_app
from hermes_threshold.config import Settings


def test_health_initializes_database(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "hermes-threshold",
        "db_ready": True,
        "scheduler_enabled": False,
    }


def test_wake_dry_run_records_draft_suggestion(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        response = client.post(
            "/wake",
            json={
                "reason": "manual",
                "dry_run": True,
                "event": {"topic": "Hermes approval tiers"},
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "ask_approval"
    assert payload["safety_risk"] == "medium"
    assert payload["recommended_action"]["title"] == "Create approval gate note"

    counts = app.state.store.table_counts()
    assert counts["wake_cycles"] == 1
    assert counts["suggestions"] == 1
    assert counts["approvals"] == 1


def test_scheduled_wake_without_context_sleeps(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        response = client.post("/wake", json={"reason": "scheduled", "dry_run": True})

    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "sleep"
    assert "no fresh event context" in payload["reason_summary"]


def test_event_can_trigger_dry_run_wake(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        response = client.post(
            "/events",
            json={
                "event_type": "project_note",
                "source": "test",
                "payload": {"note": "define action tiers"},
                "trigger_wake": True,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "recorded"
    assert payload["event_id"].startswith("activity_")
    assert payload["wake_decision"]["decision"] == "draft_only"

    counts = app.state.store.table_counts()
    assert counts["activity_log"] == 1
    assert counts["wake_cycles"] == 1


def test_feedback_records_rating(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        wake = client.post(
            "/wake",
            json={
                "reason": "manual",
                "dry_run": True,
                "event": {"topic": "action tiers"},
            },
        ).json()
        response = client.post(
            "/feedback",
            json={
                "cycle_id": wake["cycle_id"],
                "rating": "useful",
                "note": "Good planning boundary.",
            },
        )

    assert response.status_code == 200
    assert response.json()["feedback_id"].startswith("feedback_")
    assert app.state.store.table_counts()["feedback"] == 1
