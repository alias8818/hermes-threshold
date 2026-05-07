from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    workspace_id: str = "hermes-dev"
    user_peer_id: str = "user_jeremy"
    hermes_peer_id: str = "hermes_main"
    plugin_peer_id: str = "hermes_threshold"
    timezone_name: str = "America/Chicago"
    db_path: Path = Path("data/hermes_threshold.sqlite3")
    scheduler_enabled: bool = True
    scheduler_interval_hours: int = 3
    scheduler_jitter_seconds: int = 1800
    max_notifications_per_day: int = 1
    quiet_hours_start: int = 21
    quiet_hours_end: int = 7
    min_minutes_between_notifications: int = 240

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            workspace_id=os.getenv("HONCHO_WORKSPACE_ID", cls.workspace_id),
            user_peer_id=os.getenv("HERMES_USER_PEER_ID", cls.user_peer_id),
            hermes_peer_id=os.getenv("HERMES_PEER_ID", cls.hermes_peer_id),
            plugin_peer_id=os.getenv("HERMES_THRESHOLD_PEER_ID", cls.plugin_peer_id),
            timezone_name=os.getenv("HERMES_THRESHOLD_TIMEZONE", cls.timezone_name),
            db_path=Path(os.getenv("HERMES_THRESHOLD_DB_PATH", str(cls.db_path))),
            scheduler_enabled=_env_bool(
                "HERMES_THRESHOLD_SCHEDULER_ENABLED",
                cls.scheduler_enabled,
            ),
            scheduler_interval_hours=_env_int(
                "HERMES_THRESHOLD_SCHEDULER_INTERVAL_HOURS",
                cls.scheduler_interval_hours,
            ),
            scheduler_jitter_seconds=_env_int(
                "HERMES_THRESHOLD_SCHEDULER_JITTER_SECONDS",
                cls.scheduler_jitter_seconds,
            ),
            max_notifications_per_day=_env_int(
                "HERMES_THRESHOLD_MAX_NOTIFICATIONS_PER_DAY",
                cls.max_notifications_per_day,
            ),
            quiet_hours_start=_env_int(
                "HERMES_THRESHOLD_QUIET_HOURS_START",
                cls.quiet_hours_start,
            ),
            quiet_hours_end=_env_int(
                "HERMES_THRESHOLD_QUIET_HOURS_END",
                cls.quiet_hours_end,
            ),
            min_minutes_between_notifications=_env_int(
                "HERMES_THRESHOLD_MIN_MINUTES_BETWEEN_NOTIFICATIONS",
                cls.min_minutes_between_notifications,
            ),
        )
