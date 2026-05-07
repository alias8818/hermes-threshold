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


def test_auth_required_for_mutating_routes(tmp_path):
    app = create_app(
        Settings(
            db_path=tmp_path / "test.sqlite3",
            scheduler_enabled=False,
            auth_required=True,
            api_token="test-token",
        )
    )

    with TestClient(app) as client:
        unauthorized = client.post(
            "/events",
            json={"event_type": "note", "payload": {}},
        )
        authorized = client.post(
            "/events",
            headers={"authorization": "Bearer test-token"},
            json={"event_type": "note", "payload": {}},
        )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200


def test_suggestion_review_flow(tmp_path):
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
        suggestion_id = wake["recommended_action"]["suggestion_id"]

        drafted = client.get("/suggestions?status=drafted")
        approved = client.post(f"/suggestions/{suggestion_id}/approve")
        no_drafts = client.get("/suggestions?status=drafted")
        approved_list = client.get("/suggestions?status=approved")

    assert drafted.status_code == 200
    assert drafted.json()["suggestions"][0]["suggestion_id"] == suggestion_id
    assert approved.status_code == 200
    assert approved.json()["suggestion"]["status"] == "approved"
    assert no_drafts.json()["suggestions"] == []
    assert approved_list.json()["suggestions"][0]["suggestion_id"] == suggestion_id


def test_missing_suggestion_review_returns_404(tmp_path):
    app = create_app(Settings(db_path=tmp_path / "test.sqlite3", scheduler_enabled=False))

    with TestClient(app) as client:
        response = client.post("/suggestions/missing/approve")

    assert response.status_code == 404


def test_trial_summary_counts_review_and_feedback(tmp_path):
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
        suggestion_id = wake["recommended_action"]["suggestion_id"]
        client.post(f"/suggestions/{suggestion_id}/dismiss")
        client.post(
            "/feedback",
            json={
                "cycle_id": wake["cycle_id"],
                "suggestion_id": suggestion_id,
                "rating": "too_much",
            },
        )
        response = client.get("/trial-summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["counts"]["wake_cycles"] == 1
    assert payload["dismissed_suggestions"] == 1
    assert payload["annoyance_feedback"] == 1
