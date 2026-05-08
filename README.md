# Hermes Threshold

Hermes Threshold is the first MVP slice from `plan-details.md`: a restrained
FastAPI service that decides whether Hermes should sleep, reflect, draft,
notify, or request approval during proactive wake cycles.

The current implementation is deliberately local and auditable:

- `/health` initializes and reports SQLite-backed service state.
- `/wake` runs a deterministic MVP wake decision and stores the result.
- `/events` records incoming context events for later decision cycles.
- `/feedback` records user feedback for suggestions and wake outcomes.
- `/suggestions` lets Hermes review, approve, or dismiss drafted suggestions.
- `/trial-summary` reports controlled-trial counters.
- APScheduler wiring exists for local randomized wakes, but real user-facing
  notifications are not enabled yet.

## Run

```bash
uv run uvicorn hermes_threshold.app:app --reload
```

Useful defaults can be overridden with environment variables:

- `HERMES_THRESHOLD_DB_PATH`
- `HERMES_THRESHOLD_SCHEDULER_ENABLED`
- `HERMES_THRESHOLD_SCHEDULER_INTERVAL_SECONDS`
- `HERMES_THRESHOLD_SCHEDULER_EVENT_NOTE`
- `HERMES_THRESHOLD_MAX_NOTIFICATIONS_PER_DAY`
- `HERMES_THRESHOLD_QUIET_HOURS_START`
- `HERMES_THRESHOLD_QUIET_HOURS_END`
- `HERMES_THRESHOLD_API_TOKEN`
- `HERMES_THRESHOLD_AUTH_REQUIRED`
- `HONCHO_API_KEY`

## Hermes Integration

Use [docs/hermes-integration.md](docs/hermes-integration.md) as the current
contract. Hermes should call `POST /events`, read `GET /suggestions`, and show
drafted suggestions for review. Outbound autonomous messaging remains disabled.
The `hermes-threshold-review` CLI provides the same review path for Hermes CLI
integration or operator testing.

The accelerated random-wake trial is complete. See
[docs/trial-readout.md](docs/trial-readout.md) for the readout. Keep
`HERMES_THRESHOLD_SCHEDULER_ENABLED=0` until Threshold is fed higher-signal
Hermes events.

## Test

```bash
uv run --extra dev pytest
```

## Current Boundary

This repository is not yet a production Hermes plugin. It implements the
planning document's initial FastAPI, persistence, wake-cycle, and structured
feedback milestones. External dispatch, LLM candidate generation, and approval
UI integration remain behind explicit implementation boundaries. The current
continuation path is event-driven drafting with stable suppression keys for
dismissed ideas, not another random-wake trial.
