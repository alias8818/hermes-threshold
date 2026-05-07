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
