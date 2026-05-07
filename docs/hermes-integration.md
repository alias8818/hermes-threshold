# Hermes Integration Contract

Hermes Threshold is a local review gate. Hermes should call it, read drafted
suggestions, and surface reviewable items to the user. Hermes Threshold should
not send autonomous outbound notifications in the current integration phase.

## Call Path

Use this path first:

1. Hermes sends noteworthy context to `POST /events`.
2. Hermes includes `trigger_wake=true` only when it wants an immediate dry-run
   threshold decision.
3. Hermes reads reviewable drafts from `GET /suggestions?status=drafted`.
4. Hermes surfaces those drafts as cards or CLI rows.
5. User action calls `POST /suggestions/{suggestion_id}/approve`,
   `POST /suggestions/{suggestion_id}/dismiss`, or `POST /feedback`.
6. Operators inspect trial counters with `GET /trial-summary` or the
   `hermes-threshold-review summary` CLI.

This keeps Hermes in control of presentation while Hermes Threshold owns
scoring, safety gating, and audit persistence.

## Authentication

Set `HERMES_THRESHOLD_API_TOKEN` and `HERMES_THRESHOLD_AUTH_REQUIRED=1` before
exposing the service outside a private localhost-only setup.

Hermes may authenticate either way:

```http
Authorization: Bearer <token>
```

or:

```http
X-Hermes-Threshold-Token: <token>
```

## Endpoints

### `POST /events`

Records context from Hermes. Use `trigger_wake=true` for a dry-run decision.

```json
{
  "event_type": "conversation_note",
  "source": "hermes",
  "payload": {
    "note": "The user is refining Hermes autonomy action tiers."
  },
  "trigger_wake": true
}
```

### `GET /suggestions?status=drafted`

Returns drafted suggestions Hermes can show for review.

### `POST /suggestions/{suggestion_id}/approve`

Marks a suggestion as approved. Hermes can then decide how to present or act on
that approved suggestion.

### `POST /suggestions/{suggestion_id}/dismiss`

Marks a suggestion as dismissed. Hermes should avoid resurfacing dismissed
items.

### `POST /feedback`

Records user feedback such as `useful`, `not_useful`, `too_much`,
`wrong_memory`, or `save`.

### `GET /trial-summary`

Returns wake, suggestion, feedback, useful, and annoyance counters for the
current controlled trial.

## CLI Review Path

Hermes or an operator can review drafts without reading SQLite directly:

```bash
hermes-threshold-review list --status drafted
hermes-threshold-review approve suggestion_123
hermes-threshold-review dismiss suggestion_456
hermes-threshold-review summary
```

## Honcho Boundary

Hermes Threshold performs read-only Honcho retrieval when `HONCHO_API_KEY` is
available. If Honcho is unavailable, decisions continue from the event payload
and record that fallback in the decision context. The service does not write to
Honcho in this phase.

## Controlled Trial

For the first trial, leave outbound notifications disabled and review drafts
manually once per day:

```bash
curl -fsS http://127.0.0.1:8789/suggestions?status=drafted \
  -H "Authorization: Bearer $HERMES_THRESHOLD_API_TOKEN"
```

or:

```bash
hermes-threshold-review summary
```

Track:

- wake count
- drafted suggestion count
- dismissed or annoying suggestion count
- approved or useful suggestion count

For an accelerated local trial, set:

```bash
HERMES_THRESHOLD_SCHEDULER_INTERVAL_SECONDS=300
HERMES_THRESHOLD_SCHEDULER_JITTER_SECONDS=0
```

The scheduler still uses `dry_run=true`, so it creates reviewable drafts without
dispatching outbound messages.
