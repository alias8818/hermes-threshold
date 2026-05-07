# Hermes Threshold

Hermes Threshold is the first MVP slice from `plan-details.md`: a restrained
FastAPI service that decides whether Hermes should sleep, reflect, draft,
notify, or request approval during proactive wake cycles.

The current implementation is deliberately local and auditable:

- `/health` initializes and reports SQLite-backed service state.
- `/wake` runs a deterministic MVP wake decision and stores the result.
- `/events` records incoming context events for later decision cycles.
- `/feedback` records user feedback for suggestions and wake outcomes.
- APScheduler wiring exists for local randomized wakes, but real user-facing
  notifications and Honcho/Hermes calls are not enabled yet.

## Run

```bash
uv run uvicorn hermes_threshold.app:app --reload
```

Useful defaults can be overridden with environment variables:

- `HERMES_THRESHOLD_DB_PATH`
- `HERMES_THRESHOLD_SCHEDULER_ENABLED`
- `HERMES_THRESHOLD_MAX_NOTIFICATIONS_PER_DAY`
- `HERMES_THRESHOLD_QUIET_HOURS_START`
- `HERMES_THRESHOLD_QUIET_HOURS_END`

## Test

```bash
uv run --extra dev pytest
```

## Current Boundary

This repository is not yet a production Hermes plugin. It implements the
planning document's initial FastAPI, persistence, wake-cycle, and structured
feedback milestones. External dispatch, Honcho retrieval, LLM candidate
generation, and approval UI integration remain behind explicit implementation
boundaries.
