from __future__ import annotations

import asyncio

from hermes_threshold.config import Settings
from hermes_threshold.engine import ThresholdEngine
from hermes_threshold.models import WakeRequest
from hermes_threshold.store import SQLiteStore


def test_critic_blocks_intrusive_wording(tmp_path):
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.init_schema()
    engine = ThresholdEngine(Settings(db_path=tmp_path / "test.sqlite3"), store)

    decision = engine._decision(
        cycle_id="cycle_test",
        decision="notify_user",
        confidence=0.9,
        user_value_score=7,
        interruption_cost_score=5,
        novelty_score=4,
        memory_confidence=0.8,
        safety_risk="low",
        reason_summary="Candidate looked useful.",
        recommended_action={
            "title": "Check in",
            "description": "I noticed you seemed stressed late last night.",
        },
    )

    criticized = engine._critic(decision)

    assert criticized.decision == "reflect_only"
    assert criticized.safety_risk == "medium"


def test_quiet_hours_reflects_only(tmp_path):
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.init_schema()
    engine = ThresholdEngine(
        Settings(
            db_path=tmp_path / "test.sqlite3",
            quiet_hours_start=0,
            quiet_hours_end=23,
        ),
        store,
    )

    decision = asyncio.run(
        engine.run_wake_cycle(
            WakeRequest(reason="scheduled", dry_run=True, event={"topic": "action tiers"})
        )
    )

    assert decision.decision == "reflect_only"
    assert "Quiet hours" in decision.reason_summary


def test_suppression_key_reuses_dismissed_suggestion_across_copy_changes(tmp_path):
    store = SQLiteStore(tmp_path / "test.sqlite3")
    store.init_schema()
    engine = ThresholdEngine(Settings(db_path=tmp_path / "test.sqlite3"), store)
    request = WakeRequest(
        reason="event:follow_up_request",
        dry_run=True,
        event={"thread_id": "same-follow-up"},
    )

    first = engine._decision(
        cycle_id="cycle_first",
        decision="draft_only",
        confidence=0.8,
        user_value_score=8,
        interruption_cost_score=3,
        novelty_score=5,
        memory_confidence=0.7,
        safety_risk="low",
        reason_summary="Draft a follow-up.",
        recommended_action={
            "title": "Capture follow-up",
            "description": "Original follow-up copy.",
            "suppression_key": "follow-up:same-follow-up",
        },
    )
    second = engine._decision(
        cycle_id="cycle_second",
        decision="draft_only",
        confidence=0.8,
        user_value_score=8,
        interruption_cost_score=3,
        novelty_score=5,
        memory_confidence=0.7,
        safety_risk="low",
        reason_summary="Draft a follow-up.",
        recommended_action={
            "title": "Capture follow-up",
            "description": "Reworded follow-up copy.",
            "suppression_key": "follow-up:same-follow-up",
        },
    )

    store.record_wake_cycle(first, request)
    suggestion_id = first.recommended_action["suggestion_id"]
    store.update_suggestion_status(suggestion_id, "dismissed")
    store.record_wake_cycle(second, request)

    assert second.recommended_action["suggestion_id"] == suggestion_id
    assert second.recommended_action["existing_suggestion_status"] == "dismissed"
    assert store.trial_summary()["drafted_suggestions"] == 0
    assert store.trial_summary()["dismissed_suggestions"] == 1
