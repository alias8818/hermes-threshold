from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from hermes_threshold.models import FeedbackRequest, Suggestion, WakeDecision, WakeRequest


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
                    suppression_key TEXT,
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
            self._ensure_column(db, "suggestions", "suppression_key", "TEXT")
            db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_suggestions_suppression_key
                ON suggestions(suppression_key)
                """
            )

    def _ensure_column(
        self,
        db: sqlite3.Connection,
        table: str,
        column: str,
        definition: str,
    ) -> None:
        columns = {
            str(row["name"])
            for row in db.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

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
            suggestion_id: str | None = None
            should_insert_suggestion = False
            if action:
                title = str(action.get("title", "Untitled suggestion"))
                description = str(action.get("description", ""))
                suppression_key = action.get("suppression_key")
                if suppression_key is not None:
                    suppression_key = str(suppression_key)
                existing_suggestion = self._find_existing_suggestion(
                    db,
                    title,
                    description,
                    suppression_key,
                )
                provided_suggestion_id = action.get("suggestion_id")
                suggestion_id = provided_suggestion_id or existing_suggestion["suggestion_id"]
                if suggestion_id is None:
                    suggestion_id = f"suggestion_{uuid.uuid4().hex}"
                    should_insert_suggestion = True
                elif provided_suggestion_id and existing_suggestion["suggestion_id"] is None:
                    should_insert_suggestion = True
                action["suggestion_id"] = suggestion_id
                if existing_suggestion["status"]:
                    action["existing_suggestion_status"] = existing_suggestion["status"]

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
            if action and should_insert_suggestion:
                db.execute(
                    """
                    INSERT INTO suggestions (
                        suggestion_id, cycle_id, created_at, title,
                        description, suppression_key, status, payload_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        suggestion_id,
                        decision.cycle_id,
                        decision.created_at.isoformat(),
                        str(action.get("title", "Untitled suggestion")),
                        str(action.get("description", "")),
                        action.get("suppression_key"),
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

    def _find_existing_suggestion(
        self,
        db: sqlite3.Connection,
        title: str,
        description: str,
        suppression_key: str | None,
    ) -> dict[str, str | None]:
        if suppression_key:
            row = db.execute(
                """
                SELECT suggestion_id, status
                FROM suggestions
                WHERE suppression_key = ?
                ORDER BY
                  CASE status
                    WHEN 'drafted' THEN 0
                    WHEN 'dismissed' THEN 1
                    WHEN 'approved' THEN 2
                    ELSE 3
                  END,
                  created_at DESC
                LIMIT 1
                """,
                (suppression_key,),
            ).fetchone()
            if row is not None:
                return {"suggestion_id": str(row["suggestion_id"]), "status": str(row["status"])}
            return {"suggestion_id": None, "status": None}

        row = db.execute(
            """
            SELECT suggestion_id, status
            FROM suggestions
            WHERE title = ?
              AND description = ?
            ORDER BY
              CASE status
                WHEN 'drafted' THEN 0
                WHEN 'dismissed' THEN 1
                WHEN 'approved' THEN 2
                ELSE 3
              END,
              created_at DESC
            LIMIT 1
            """,
            (title, description),
        ).fetchone()
        if row is None:
            return {"suggestion_id": None, "status": None}
        return {"suggestion_id": str(row["suggestion_id"]), "status": str(row["status"])}

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

    def list_suggestions(self, status: str | None = None, limit: int = 50) -> list[Suggestion]:
        query = """
            SELECT suggestion_id, cycle_id, created_at, title, description, status, payload_json
            FROM suggestions
        """
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self.connect() as db:
            rows = db.execute(query, params).fetchall()
        return [self._suggestion_from_row(row) for row in rows]

    def update_suggestion_status(self, suggestion_id: str, status: str) -> Suggestion | None:
        with self.connect() as db:
            row = db.execute(
                """
                SELECT suggestion_id
                FROM suggestions
                WHERE suggestion_id = ?
                """,
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None
            db.execute(
                """
                UPDATE suggestions
                SET status = ?
                WHERE suggestion_id = ?
                """,
                (status, suggestion_id),
            )
            updated = db.execute(
                """
                SELECT suggestion_id, cycle_id, created_at, title, description, status, payload_json
                FROM suggestions
                WHERE suggestion_id = ?
                """,
                (suggestion_id,),
            ).fetchone()
        return self._suggestion_from_row(updated)

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

    def trial_summary(self) -> dict[str, int]:
        counts = self.table_counts()
        with self.connect() as db:
            drafted = db.execute(
                "SELECT COUNT(*) AS count FROM suggestions WHERE status = 'drafted'"
            ).fetchone()["count"]
            approved = db.execute(
                "SELECT COUNT(*) AS count FROM suggestions WHERE status = 'approved'"
            ).fetchone()["count"]
            dismissed = db.execute(
                "SELECT COUNT(*) AS count FROM suggestions WHERE status = 'dismissed'"
            ).fetchone()["count"]
            useful = db.execute(
                "SELECT COUNT(*) AS count FROM feedback WHERE rating IN ('useful', 'save')"
            ).fetchone()["count"]
            annoyance = db.execute(
                "SELECT COUNT(*) AS count FROM feedback WHERE rating IN ('not_useful', 'too_much', 'wrong_memory')"
            ).fetchone()["count"]
        return {
            **counts,
            "drafted_suggestions": int(drafted),
            "approved_suggestions": int(approved),
            "dismissed_suggestions": int(dismissed),
            "useful_feedback": int(useful),
            "annoyance_feedback": int(annoyance),
        }

    def _suggestion_from_row(self, row: sqlite3.Row) -> Suggestion:
        return Suggestion(
            suggestion_id=str(row["suggestion_id"]),
            cycle_id=str(row["cycle_id"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            title=str(row["title"]),
            description=str(row["description"]),
            status=str(row["status"]),
            payload=json.loads(str(row["payload_json"])),
        )
