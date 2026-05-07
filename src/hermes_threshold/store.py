from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from hermes_threshold.models import FeedbackRequest, WakeDecision, WakeRequest


def utc_now() -> datetime:
    return datetime.now(UTC)


class SQLiteStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def init_schema(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS activity_log (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS wake_cycles (
                    cycle_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    dry_run INTEGER NOT NULL,
                    decision TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    user_value_score INTEGER NOT NULL,
                    interruption_cost_score INTEGER NOT NULL,
                    novelty_score INTEGER NOT NULL,
                    memory_confidence REAL NOT NULL,
                    safety_risk TEXT NOT NULL,
                    reason_summary TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    recommended_action_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS suggestions (
                    suggestion_id TEXT PRIMARY KEY,
                    cycle_id TEXT NOT NULL REFERENCES wake_cycles(cycle_id),
                    created_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    cycle_id TEXT NOT NULL REFERENCES wake_cycles(cycle_id),
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    cycle_id TEXT NOT NULL,
                    suggestion_id TEXT,
                    created_at TEXT NOT NULL,
                    rating TEXT NOT NULL,
                    note TEXT
                );

                CREATE TABLE IF NOT EXISTS personality_versions (
                    version_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS budgets (
                    budget_date TEXT PRIMARY KEY,
                    notifications_sent INTEGER NOT NULL DEFAULT 0,
                    max_notifications INTEGER NOT NULL
                );
                """
            )

    def record_activity(
        self,
        activity_type: str,
        source: str,
        payload: dict[str, Any],
    ) -> str:
        activity_id = f"activity_{uuid.uuid4().hex}"
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO activity_log (
                    id, created_at, activity_type, source, payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    activity_id,
                    utc_now().isoformat(),
                    activity_type,
                    source,
                    json.dumps(payload, sort_keys=True),
                ),
            )
        return activity_id

    def record_wake_cycle(self, decision: WakeDecision, request: WakeRequest) -> None:
        action = decision.recommended_action
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO wake_cycles (
                    cycle_id, created_at, reason, dry_run, decision, confidence,
                    user_value_score, interruption_cost_score, novelty_score,
                    memory_confidence, safety_risk, reason_summary, request_json,
                    recommended_action_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision.cycle_id,
                    decision.created_at.isoformat(),
                    request.reason,
                    int(request.dry_run),
                    decision.decision,
                    decision.confidence,
                    decision.user_value_score,
                    decision.interruption_cost_score,
                    decision.novelty_score,
                    decision.memory_confidence,
                    decision.safety_risk,
                    decision.reason_summary,
                    request.model_dump_json(),
                    json.dumps(action, sort_keys=True),
                ),
            )
            if action:
                suggestion_id = action.get("suggestion_id") or f"suggestion_{uuid.uuid4().hex}"
                action["suggestion_id"] = suggestion_id
                db.execute(
                    """
                    INSERT INTO suggestions (
                        suggestion_id, cycle_id, created_at, title,
                        description, status, payload_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        suggestion_id,
                        decision.cycle_id,
                        decision.created_at.isoformat(),
                        str(action.get("title", "Untitled suggestion")),
                        str(action.get("description", "")),
                        "drafted",
                        json.dumps(action, sort_keys=True),
                    ),
                )
            if decision.decision == "ask_approval":
                db.execute(
                    """
                    INSERT INTO approvals (
                        approval_id, cycle_id, created_at, status, payload_json
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        f"approval_{uuid.uuid4().hex}",
                        decision.cycle_id,
                        decision.created_at.isoformat(),
                        "pending",
                        json.dumps(action, sort_keys=True),
                    ),
                )

    def record_feedback(self, feedback: FeedbackRequest) -> str:
        feedback_id = f"feedback_{uuid.uuid4().hex}"
        with self.connect() as db:
            db.execute(
                """
                INSERT INTO feedback (
                    feedback_id, cycle_id, suggestion_id, created_at, rating, note
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    feedback.cycle_id,
                    feedback.suggestion_id,
                    utc_now().isoformat(),
                    feedback.rating,
                    feedback.note,
                ),
            )
        return feedback_id

    def notification_count_for(self, day: date) -> int:
        with self.connect() as db:
            row = db.execute(
                """
                SELECT COUNT(*) AS count
                FROM wake_cycles
                WHERE decision = 'notify_user'
                  AND dry_run = 0
                  AND substr(created_at, 1, 10) = ?
                """,
                (day.isoformat(),),
            ).fetchone()
        return int(row["count"])

    def table_counts(self) -> dict[str, int]:
        tables = [
            "activity_log",
            "wake_cycles",
            "suggestions",
            "approvals",
            "feedback",
            "personality_versions",
            "budgets",
        ]
        with self.connect() as db:
            return {
                table: int(db.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"])
                for table in tables
            }
