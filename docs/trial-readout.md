# Hermes Threshold Trial Readout

Captured after the accelerated controlled trial on 2026-05-08.

## Result

- Wake cycles: 236
- Suggestions generated: 23
- Suggestions dismissed: 23
- Drafts remaining: 0
- Suggestions approved: 0

## Conclusion

Accelerated random wakes are not useful enough by themselves. The trial mostly
produced repeated low-value autonomy-policy drafts, and every generated
suggestion was dismissed. Threshold should stay available as a review gate, but
the scheduler should remain off until Hermes feeds better input signals.

## Next Operating Mode

Keep `HERMES_THRESHOLD_SCHEDULER_ENABLED=0`.

Use event-driven Threshold calls for high-signal Hermes events only:

- `remember_this`: the user explicitly asks Hermes to remember something.
- `follow_up_request`: the user asks Hermes to follow up later.
- `open_loop_detected`: Hermes identifies a real unresolved promise, task, or
  decision.
- `project_state_changed`: a project or task changes state in a way Hermes may
  need to remember.
- `suggestion_reviewed`: the user approves or dismisses a prior Threshold
  suggestion.

Threshold's next job is to answer whether a real event is worth drafting for
review, not to invent proactive ideas on a timer.
