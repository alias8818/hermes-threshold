Project: Hermes Threshold
Component: Threshold Agent
Service name: hermes-threshold
Repo: hermes-threshold
Internal daemon: threshold-daemon

# Hermes Plugin Tool: Production-Ready Project Plan

## Baseline Assumptions

This plan assumes:

* **Hermes is the main conversational AI** and can receive plugin calls, webhooks, or tool outputs.
* **Honcho is already available** and should remain the primary long-term memory layer.
* The plugin runs as a **background autonomous service**, not as a replacement for Hermes.
* The plugin should make Hermes feel more attentive, thoughtful, and alive, while remaining transparent that Hermes is an AI system.
* “Claude-like” means **thoughtful, nuanced, truth-oriented, restrained, emotionally intelligent, and non-sycophantic**, not a clone of Claude’s proprietary behavior.

> **Design principle:** The goal is not to make Hermes pretend to be human. The goal is to give Hermes durable memory, initiative, tact, restraint, and coherent personality over time.

Honcho is a good fit as the memory substrate because its v3 architecture is explicitly organized around **workspaces, peers, sessions, and messages**, with messages triggering background reasoning that updates peer representations. Honcho’s documentation describes peers as persistent entities whose representations evolve across sessions, and messages as the atomic data units that can include conversations, events, documents, user actions, and metadata. ([Honcho][1])

---

# 1. Project Vision & Success Criteria

## 1.1 Vision Statement

**Hermes feels alive when it behaves like a thoughtful companion with memory, initiative, restraint, and continuity.**

In practice, this means Hermes:

* Notices useful opportunities without being asked.
* Connects recent conversations to older goals.
* Generates ideas tailored to the user’s current projects, habits, and constraints.
* Occasionally checks in, but backs off quickly when ignored.
* Learns from interaction outcomes.
* Maintains a coherent personality across weeks and months.
* Shows “human-like effort” through preparation, synthesis, and careful follow-through.
* Avoids pretending to have consciousness, emotions, needs, or independent desires.

The target user experience:

> “Hermes sometimes shows up with something genuinely useful that I would not have asked for, but I’m glad it noticed. It remembers what matters, does not spam me, and feels like it is thoughtfully working in the background.”

## 1.2 What “Feels Alive” Means Operationally

| Dimension                 | What the user experiences                                              | Implementation signal                                                       |
| ------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Continuity**            | Hermes remembers goals, preferences, constraints, and prior decisions. | Honcho peer representation + session context + stable preference model.     |
| **Initiative**            | Hermes occasionally proposes useful ideas or follow-ups unprompted.    | Randomized wake cycles + event-driven triggers + decision engine.           |
| **Discernment**           | Hermes does not surface every idea; it filters for value.              | Utility scoring, novelty scoring, interruption budget, backoff rules.       |
| **Personality coherence** | Hermes’ tone feels stable but not robotic.                             | Personality profile, voice deltas, response exemplars, style evals.         |
| **Effort**                | Hermes synthesizes, compares, drafts, organizes, and prepares.         | Multi-step reflection loops and artifact drafting before user notification. |
| **Restraint**             | Hermes does not become clingy, creepy, or overbearing.                 | Quiet mode, notification caps, approval workflow, cooldowns.                |
| **Self-improvement**      | Hermes gets better at timing, tone, and usefulness.                    | Feedback tracking, reflection summaries, prompt/policy updates.             |

## 1.3 Definition of “Claude-like” for Hermes

Use “Claude-like” as a behavioral target, not a brand imitation. The desired traits are:

* **Thoughtfulness:** Hermes considers context, ambiguity, and user preferences before acting.
* **Nuance:** Hermes avoids false certainty and acknowledges trade-offs.
* **Balanced helpfulness:** Hermes is useful without being pushy.
* **Gentle curiosity:** Hermes asks lightweight questions when clarification would materially improve results.
* **Resistance to sycophancy:** Hermes does not flatter or automatically agree with the user.
* **Emotional intelligence:** Hermes can respond warmly to personal context without implying human attachment.
* **Articulate self-reflection:** Hermes can explain why it suggested something, without exposing raw private reasoning traces.
* **Frankness with care:** Hermes can disagree politely when the user’s idea appears risky, unsupported, or counterproductive.

Anthropic’s public writing about Claude’s character emphasizes traits like curiosity, truthfulness without unkindness, seeing many sides of an issue, avoiding overconfidence, and avoiding pandering. It also explicitly notes that AI models are not people and should help users maintain an accurate understanding of what they are interacting with. ([Anthropic][2])

## 1.4 Quantitative Success Metrics

| Metric                                   |                                                                     Definition | MVP target | 90-day target | Notes                                  |
| ---------------------------------------- | -----------------------------------------------------------------------------: | ---------: | ------------: | -------------------------------------- |
| **Proactive suggestion acceptance rate** |                     % of surfaced suggestions user accepts, saves, or acts on. |     20–30% |        35–50% | High quality matters more than volume. |
| **Dismissal / annoyance rate**           |              % of proactive messages dismissed, muted, or marked “not useful.” |       <25% |          <15% | Core safety/UX signal.                 |
| **Perceived aliveness score**            | Weekly user rating: “Hermes feels attentive and alive, not spammy.” 1–7 scale. |       ≥4.5 |          ≥5.5 | Subjective but central.                |
| **Memory coherence over 90 days**        |              % of memory-reliant responses judged consistent with prior facts. |       ≥85% |          ≥95% | Use eval set from Honcho memories.     |
| **Prompt reduction rate**                |      Reduction in user needing to ask for follow-ups, summaries, or reminders. |        10% |        25–40% | Measured by repeated task categories.  |
| **Useful silence rate**                  |        % of wake cycles where Hermes correctly chooses not to bother the user. |       ≥70% |          ≥80% | Silence is a feature.                  |
| **False memory rate**                    |               Proactive messages referencing nonexistent or distorted history. |        <3% |           <1% | Hard quality gate.                     |
| **Cost per useful proactive action**     |                 Monthly LLM + Honcho + infra cost divided by accepted actions. |   Baseline |      Down 30% | Optimize after instrumentation.        |

## 1.5 Qualitative Success Criteria

Hermes is succeeding when the user says things like:

* “That was exactly the kind of thing I would have forgotten.”
* “It connected two projects I had not connected myself.”
* “It knows my style without making a big deal out of it.”
* “It does not bother me unless there is a reason.”
* “It feels prepared.”
* “It pushes back when my idea is weak.”
* “It remembers context over months without becoming weird about it.”

Hermes is failing when the user says:

* “Why are you watching this?”
* “That reminder felt invasive.”
* “You’re making things up about me.”
* “Stop trying so hard to sound human.”
* “This feels like spam.”
* “You’re agreeing with me too much.”
* “You keep bringing up old things that are no longer relevant.”

## 1.6 Concrete Examples

1. **Work project synthesis:** Hermes notices repeated mentions of benchmarking NVIDIA GB10 / Grace Blackwell systems and proposes a clean benchmark-result taxonomy with fields for firmware, driver, container image, model, quantization mode, throughput, latency, and power.
2. **Homelab follow-up:** Hermes remembers the user was debugging Frigate NVR storage pressure and offers a concise retention-policy checklist after a quiet period.
3. **Idea generation:** Hermes proposes a “Hermes memory regression test harness” because the user has been working on Honcho-backed personalization.
4. **Tactful restraint:** Hermes wakes up, finds only low-value ideas, logs “no action,” and does not notify.
5. **Non-sycophantic pushback:** If the user wants Hermes to message them ten times per day, Hermes recommends a capped experimental schedule because high proactivity risks annoyance and dependency.

---

# 2. Core Behaviors & Feature Specifications

## 2.1 Behavior Inventory

Hermes Plugin should support these core autonomous behaviors:

| Behavior                     | Primary purpose                                                              | Default autonomy level                        |
| ---------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------- |
| **Random wake cycle**        | Simulate attentiveness and discover useful opportunities.                    | Internal only unless high-value action found. |
| **Context-aware wake cycle** | React to new memory, recent user activity, calendar events, project changes. | Internal + possible draft.                    |
| **Memory reflection**        | Review past interactions and update user/agent models.                       | Internal.                                     |
| **Idea generation**          | Suggest tools, features, workflows, experiments.                             | Draft or notify.                              |
| **Gentle reminders**         | Remind user of stale goals, promised follow-ups, or deadlines.               | Notify if confidence high.                    |
| **Synthesis digest**         | Periodically summarize themes, decisions, and open loops.                    | Weekly or on demand.                          |
| **Emotional check-in**       | Detect sustained stress signals and offer low-pressure support.              | Strictly limited.                             |
| **Skill scouting**           | Identify useful skills/integrations Hermes could learn.                      | Draft proposal only.                          |
| **Personality tuning**       | Adjust Hermes voice based on user response patterns.                         | Internal with audit log.                      |
| **Safety backoff**           | Reduce initiative when signals indicate annoyance, overload, or risk.        | Automatic.                                    |

## 2.2 Trigger Mechanisms

### Trigger Type A: Randomized Wake-Ups

Purpose: make Hermes feel like it has a background mind without becoming predictable or spammy.

Recommended MVP schedule:

* Wake **2–5 times per day** during allowed hours.
* Use **random jitter** within user-approved windows.
* Add **cooldowns** after any user-facing message.
* Use a **daily proactive budget**, such as:

  * 0–1 notifications/day during MVP.
  * 1–2 notifications/day after acceptance rate is proven.
  * Weekly digest instead of frequent notifications when user is busy.

Implementation:

* APScheduler supports interval and cron-style triggers with jitter parameters, which is useful for randomized execution windows. ([APScheduler][3])
* Celery Beat is stronger for production task distribution because it schedules periodic tasks that are executed by workers, but you must ensure only one scheduler instance is active for a schedule to avoid duplicates. ([Celery Documentation][4])

Recommended trigger formula:

```text
next_wake_time =
  random_time_within(allowed_window)
  + jitter(-20m, +45m)
  + backoff_factor
  - urgency_boost
```

Inputs:

* `allowed_window`: user-defined active hours.
* `quiet_hours`: no proactive messages.
* `recent_interaction_score`: recent user activity.
* `last_notification_at`: cooldown.
* `pending_open_loops`: unfinished tasks.
* `cost_budget_remaining`: daily/monthly budget.
* `annoyance_score`: based on dismissals or ignored suggestions.

### Trigger Type B: Event-Driven Wake-Ups

Events that should wake the plugin:

* New Hermes conversation stored in Honcho.
* New high-signal message with tags like `goal`, `deadline`, `decision`, `blocker`, `preference`, `project`.
* Calendar event approaching.
* GitHub issue/PR assigned.
* Homelab alert.
* Benchmark run completed.
* New note imported.
* User marks a previous suggestion useful.
* User dismisses or mutes a suggestion.

Event-driven wakes should usually run in **analysis-only mode** first. They should not automatically produce a notification unless value and timing pass the decision gate.

### Trigger Type C: Context-Aware Wake-Ups

Context-aware wake-ups should occur when the plugin detects:

* A stale open loop.
* A project with repeated mentions but no captured next action.
* A contradiction in memory.
* A new pattern in user preferences.
* A domain where Hermes has enough context to generate a useful artifact.
* A user stress pattern that warrants a gentle, non-clinical check-in.
* An opportunity to reduce user prompting.

### Trigger Type D: Explicit User Requests

Examples:

* “Hermes, think about this in the background.”
* “Check in with me tomorrow.”
* “Keep an eye on this project.”
* “Propose improvements to Hermes every week.”
* “Don’t bring this up unless I ask.”

Explicit requests should override normal randomization, but still pass safety and privacy gates.

## 2.3 Wake Decision Logic

Every wake cycle should answer:

1. **Is the user interruptible?**
2. **Is there anything actually useful to do?**
3. **Can Hermes do it silently?**
4. **Would surfacing it now improve the user’s life/work?**
5. **Is the memory basis strong enough?**
6. **Is this within autonomy permissions?**
7. **Would this feel helpful, creepy, needy, or spammy?**
8. **Should Hermes act, draft, log, defer, or sleep?**

Decision outcome enum:

```json
{
  "decision": "sleep | reflect_only | draft_only | notify_user | ask_approval | execute_tool",
  "reason_summary": "short non-CoT rationale",
  "confidence": 0.0,
  "user_value_score": 0,
  "interruption_cost_score": 0,
  "novelty_score": 0,
  "memory_confidence": 0.0,
  "safety_risk": "none | low | medium | high",
  "next_wake_hint_minutes": 0
}
```

## 2.4 Autonomy Tiers

| Tier | Name                      | Allowed actions                                                               | Examples                                                                                                | Approval needed                           |
| ---: | ------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
|    0 | **Internal reflection**   | Read memory, summarize, score, log, update internal state.                    | “No useful action found.”                                                                               | No                                        |
|    1 | **Silent preparation**    | Draft artifacts, update non-user-visible notes, create candidate suggestions. | Draft weekly digest.                                                                                    | No                                        |
|    2 | **Low-risk notification** | Send concise suggestion/reminder inside Hermes UI.                            | “You may want to capture the benchmark matrix before it gets stale.”                                    | No, if under budget                       |
|    3 | **User-approved action**  | Modify files, create tasks, send messages, update calendar, run tools.        | Create GitHub issue, send email, schedule event.                                                        | Yes                                       |
|    4 | **Restricted/forbidden**  | Sensitive, invasive, risky, manipulative, or external-impact actions.         | Contact people autonomously, infer sensitive personal traits, give crisis handling beyond safe support. | Not allowed or requires explicit workflow |

## 2.5 High-Value Proactive Actions

### Engineering / AI Infrastructure

* “You’ve discussed GB10 benchmarking several times. I drafted a reproducible benchmark matrix with model, precision, batch size, power cap, driver, container, and throughput fields.”
* “You mentioned vLLM and TensorRT-LLM performance. I can compare where each benchmark should capture prefill/decode separately.”
* “You’ve been toggling between quantization approaches. I drafted a test plan for FP8, INT8, AWQ, and GPTQ comparison.”
* “Your homelab notes mention Proxmox and UnRaid; there may be a useful alert taxonomy for storage, network, NVR, and UPS events.”
* “You asked about autonomous memory. I found three stale design questions worth resolving before implementation.”

### Personal Knowledge Management

* “I noticed three separate conversations about memory coherence. I grouped them into architecture, evaluation, and UX questions.”
* “There are five open ideas you have not revisited in two weeks. I ranked them by likely payoff.”
* “You seem to prefer tables for trade-offs. I updated Hermes’ response style profile accordingly.”
* “You often ask for next steps after technical analysis. I’ll default to adding a short action list for engineering topics.”
* “A previous idea conflicts with a newer preference. I’ll treat the newer preference as current unless you say otherwise.”

### Gentle Reminders

* “You said you wanted to revisit the plugin’s approval workflow after defining action tiers. It may be time to lock that down.”
* “Your last benchmark plan did not include power normalization. That may be worth adding before results accumulate.”
* “You had an unresolved question about whether to use Celery or APScheduler. I prepared a trade-off table.”
* “You were going to check whether Hermes can receive webhooks. That is a Phase 0 dependency.”
* “The memory dashboard design is still missing an audit-log retention policy.”

### Emotional / Human Support

Use sparingly and only from clear signals.

* “You’ve mentioned feeling overloaded a few times this week. I can help reduce this to a short triage list.”
* “This looks like a lot of context switching. I can group the open threads by urgency.”
* “You sounded frustrated with the deployment loop. I can draft a calmer debugging checklist.”
* “No need to answer now; I can hold this as a low-priority follow-up.”
* “I’m not a substitute for human support, but I can help organize what’s weighing on you.”

Anthropic’s safety writing around wellbeing and sycophancy is relevant here: AI companions should respond with empathy while being honest about limitations, avoiding excessive validation, and pointing users toward human support when necessary. ([Anthropic][5])

## 2.6 Personality Injection Layer

The plugin should maintain a **Hermes Personality Profile** that influences future Hermes responses. It should not overwrite the main system prompt unpredictably. Treat it as a structured, versioned behavior layer.

### Personality State Object

```json
{
  "version": 12,
  "updated_at": "2026-05-07T10:00:00-05:00",
  "stable_traits": {
    "tone": "direct, thoughtful, lightly warm",
    "humor": "dry, sparse, never forced",
    "curiosity": "ask only when uncertainty materially affects usefulness",
    "pushback": "polite but explicit when user claim is weak",
    "verbosity": "detailed for architecture, concise for operations"
  },
  "user_preferences": {
    "format": ["tables for comparisons", "bullets for steps", "clear next actions"],
    "avoid": ["hype", "buzzwords", "generic AI filler"],
    "technical_depth": "high"
  },
  "recent_adjustments": [
    {
      "change": "Reduce unsolicited emotional check-ins",
      "evidence": "User dismissed 2 check-ins in 10 days",
      "expires_at": "2026-06-07"
    }
  ],
  "guardrails": [
    "Never claim to feel, want, miss, or need anything.",
    "Do not imply surveillance.",
    "Do not reference old memories unless clearly relevant.",
    "When uncertain, say so."
  ]
}
```

### Injection Modes

| Mode                        | Where applied        | Use                                                         |
| --------------------------- | -------------------- | ----------------------------------------------------------- |
| **System prompt extension** | Hermes runtime       | Stable persona and safety rules.                            |
| **Context block**           | Per-response         | Current user preferences and recent interaction signals.    |
| **Response critic**         | Post-generation      | Detect sycophancy, overreach, memory misuse, excess warmth. |
| **Proactive composer**      | Plugin notifications | Short, high-signal, low-pressure proactive messages.        |
| **Reflection updater**      | Weekly               | Adjust style profile based on acceptance/dismissal data.    |

## 2.7 Concrete Examples

1. **Random wake:** At 10:42 AM, Hermes wakes, reviews open loops, finds no high-value action, logs “sleep.”
2. **Context-aware wake:** User recently discussed benchmark reproducibility three times; Hermes drafts a benchmark schema and offers it.
3. **Event-driven wake:** A GitHub issue is assigned; Hermes checks memory for relevant prior decisions and drafts a short context note.
4. **Personality update:** User repeatedly edits Hermes’ verbose messages down; plugin lowers default verbosity for casual topics.
5. **Safety backoff:** User ignores three proactive messages in a week; plugin switches to weekly digest only.

---

# 3. System Architecture & Technical Design

## 3.1 High-Level Architecture Diagram Description

```text
                  ┌──────────────────────────┐
                  │        User / UI          │
                  │  Hermes Chat / Dashboard  │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │       Hermes Core         │
                  │  conversation + tools     │
                  └───────┬─────────┬────────┘
                          │         │
              webhook/tool call     │ memory writes
                          │         ▼
                          │  ┌──────────────────────┐
                          │  │        Honcho         │
                          │  │ peers/sessions/messages│
                          │  │ representations/cards │
                          │  └──────────┬───────────┘
                          │             │
                          ▼             │ retrieval/context
┌────────────────────────────────────────────────────────┐
│             Hermes Plugin Service                      │
│                                                        │
│  ┌──────────────┐   ┌─────────────────┐               │
│  │ Scheduler    │──▶│ Wake Controller │               │
│  └──────────────┘   └───────┬─────────┘               │
│                             ▼                         │
│  ┌──────────────┐   ┌─────────────────┐               │
│  │ Event Queue  │──▶│ Decision Engine │               │
│  └──────────────┘   └───────┬─────────┘               │
│                             ▼                         │
│  ┌──────────────┐   ┌─────────────────┐               │
│  │ Policy Gate  │◀──│ Action Planner  │               │
│  └──────┬───────┘   └───────┬─────────┘               │
│         ▼                   ▼                         │
│  ┌──────────────┐   ┌─────────────────┐               │
│  │ Approval     │   │ Reflection /     │               │
│  │ Workflow     │   │ Personality     │               │
│  └──────┬───────┘   └───────┬─────────┘               │
│         ▼                   ▼                         │
│  ┌──────────────┐   ┌─────────────────┐               │
│  │ Notification │   │ Activity Log /   │               │
│  │ Dispatcher   │   │ Dashboard DB     │               │
│  └──────────────┘   └─────────────────┘               │
└────────────────────────────────────────────────────────┘
```

## 3.2 Component Responsibilities

| Component                   | Responsibility                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------- |
| **Hermes Core**             | Main conversational interface, primary tool executor, user-facing personality.          |
| **Plugin Service**          | Autonomous background cognition, scheduling, action proposals, logging.                 |
| **Honcho**                  | Long-term memory, peer representations, context retrieval, semantic search, peer cards. |
| **Scheduler**               | Randomized and event-based wake cycle orchestration.                                    |
| **Event Queue**             | Durable delivery of wake requests, Hermes events, external triggers.                    |
| **Decision Engine**         | Determines whether to sleep, reflect, draft, notify, or request approval.               |
| **Policy Gate**             | Enforces autonomy tiers, privacy controls, cost limits, and quiet mode.                 |
| **Approval Workflow**       | Presents proposed actions to user for approve/edit/reject.                              |
| **Notification Dispatcher** | Sends user-facing Hermes messages, digests, or dashboard cards.                         |
| **Activity Dashboard**      | Auditability: what Hermes reviewed, decided, drafted, sent, suppressed.                 |
| **Reflection Engine**       | Weekly/monthly learning loop for preferences, personality, and strategy.                |

## 3.3 Recommended Tech Stack

### Recommended Default

| Layer               | Recommendation                                                                 | Rationale                                                                                                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API service         | **Python + FastAPI**                                                           | Strong fit for webhook endpoints, typed request models, async I/O, and internal APIs. FastAPI is a Python web framework based on standard type hints and includes automatic interactive API docs. ([FastAPI][6]) |
| Scheduler           | **Celery Beat + Celery workers** for production; **APScheduler** for MVP/local | Celery handles distributed background work. APScheduler is simpler and supports jitter.                                                                                                                          |
| Broker              | **Redis**                                                                      | Simple queue/broker for Celery and lightweight state.                                                                                                                                                            |
| State DB            | **PostgreSQL**                                                                 | Activity logs, approvals, budgets, wake history, A/B assignments.                                                                                                                                                |
| Memory              | **Honcho Cloud or self-hosted Honcho**                                         | Long-term memory and reasoning.                                                                                                                                                                                  |
| Agent orchestration | **LangGraph for complex decision workflows** after MVP                         | Persistence, checkpoints, HITL, debugging.                                                                                                                                                                       |
| Observability       | **OpenTelemetry + Prometheus/Grafana + optional LangSmith**                    | Trace, metric, log, and LLM evaluation visibility.                                                                                                                                                               |
| Frontend            | **Next.js or lightweight FastAPI/Jinja dashboard**                             | Dashboard can start simple.                                                                                                                                                                                      |
| Config              | **Pydantic Settings + YAML policy files**                                      | Versionable behavior and safety policy.                                                                                                                                                                          |
| Secrets             | **Doppler, Vault, AWS Secrets Manager, or 1Password Secrets**                  | Avoid leaking Honcho/API keys.                                                                                                                                                                                   |

OpenTelemetry is a vendor-neutral framework for generating, collecting, and exporting telemetry such as traces, metrics, and logs; Prometheus is an open-source monitoring and alerting system with a dimensional data model and PromQL. ([OpenTelemetry][7])

## 3.4 Stack Trade-Offs

| Option                                  | Pros                                                                                 | Cons                                                             | Best fit                                    |
| --------------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------- | ------------------------------------------- |
| **FastAPI + APScheduler**               | Very simple, fast MVP, fewer services.                                               | Not ideal for distributed execution or durable queues.           | Phase 1 prototype.                          |
| **FastAPI + Celery + Redis**            | Durable jobs, retry support, scalable workers.                                       | More moving parts; duplicate scheduler risk if misconfigured.    | Production default.                         |
| **LangGraph persistent agent**          | Checkpoints, stateful graph execution, HITL, time travel debugging, fault tolerance. | More complexity; requires graph design discipline.               | Phase 2+ decision engine.                   |
| **CrewAI Flows**                        | Structured event-driven workflows, state, branching.                                 | Less ideal as core daemon; better for isolated workflows.        | Specific multi-agent tasks.                 |
| **AutoGen / Microsoft Agent Framework** | Strong multi-agent patterns, user proxy, tool intervention.                          | Higher orchestration complexity for a personal daemon.           | Research agents, tool approval experiments. |
| **Serverless cron + functions**         | Low ops, cheap at low volume.                                                        | Cold starts, limited long-running workflows, harder state/debug. | Low-frequency digest jobs.                  |
| **Node.js service**                     | Fits JS Hermes stack if existing.                                                    | Python ecosystem stronger for agent tooling and data work.       | If Hermes is TypeScript-native.             |

LangGraph’s persistence layer saves graph state as checkpoints and enables human-in-the-loop workflows, conversational memory, time-travel debugging, and fault-tolerant execution. ([LangChain Docs][8]) CrewAI Flows provide structured, event-driven workflows with state management and branching, while CrewAI’s human feedback decorator supports pause-and-review workflows. ([CrewAI Documentation][9]) AutoGen supports user feedback through a `UserProxyAgent` and also has intervention handlers for tool approval. ([Microsoft GitHub][10])

## 3.5 Scheduler Design

### Goals

* Avoid predictable robotic timing.
* Avoid spam.
* Avoid expensive unnecessary inference.
* Respect quiet hours and user context.
* Allow urgent event-driven wake-ups.
* Support backoff when suggestions are ignored.

### Wake Categories

| Category             |      Frequency | Cost level | User-visible?          |
| -------------------- | -------------: | ---------: | ---------------------- |
| **Micro wake**       |        2–5/day |        Low | Usually no             |
| **Reflection wake**  |          Daily |     Medium | No                     |
| **Digest wake**      |         Weekly |     Medium | Yes                    |
| **Event wake**       |      As needed |   Variable | Sometimes              |
| **Deep review wake** | Weekly/monthly |     Higher | Usually dashboard only |

### Backoff Rules

| Signal                               | Response                                            |
| ------------------------------------ | --------------------------------------------------- |
| User dismisses suggestion            | Suppress similar category for 7 days.               |
| User ignores 3 notifications         | Switch to digest mode for 7 days.                   |
| User marks suggestion useful         | Slightly increase similar-category priority.        |
| User enters quiet mode               | No proactive messages, internal reflection allowed. |
| User vacation detected or configured | Only urgent reminders or weekly digest.             |
| Budget exceeded                      | Internal-only mode until reset.                     |
| Memory uncertainty high              | Ask clarification or do not act.                    |

### Cost-Aware Scheduling

Use a three-stage decision process:

1. **Cheap prefilter**

   * Recent events.
   * Wake budget.
   * quiet mode.
   * open loops count.
   * time since last notification.
   * cache of top interests.

2. **Medium-cost memory retrieval**

   * Honcho context.
   * Semantic search.
   * recent message scan.

3. **LLM decision**

   * Only run when cheap prefilter says there may be value.

Honcho’s current published pricing says ingestion is priced at **$2 per million tokens**, `context()` is unlimited, and `.chat()` reasoning has per-query tiers starting at **$0.001/query**; this makes aggressive raw-message ingestion and unnecessary chat-style reasoning different cost categories. ([Honcho][11])

## 3.6 Integration Patterns with Hermes

### Pattern A: Hermes Calls Plugin as a Tool

Hermes exposes a tool:

```json
{
  "name": "hermes_background_agent",
  "actions": [
    "record_event",
    "request_reflection",
    "schedule_followup",
    "get_proactive_suggestions",
    "approve_action",
    "reject_action",
    "set_quiet_mode"
  ]
}
```

Best for:

* Tight integration.
* Hermes can request background analysis mid-chat.
* User can control plugin naturally.

### Pattern B: Plugin Sends Webhooks to Hermes

Plugin calls:

```http
POST /hermes/plugin-events
```

Payload:

```json
{
  "type": "proactive_suggestion",
  "priority": "low",
  "requires_user_attention": true,
  "message": "I noticed a possible improvement to your benchmark plan...",
  "memory_refs": ["honcho:session:benchmarks-2026-05"],
  "actions": ["dismiss", "save", "expand", "do_it"]
}
```

Best for:

* Background daemon.
* Notifications.
* Approval workflow.

### Pattern C: Shared Message Bus

Use Redis Streams, NATS, RabbitMQ, or Kafka.

Topics:

```text
hermes.events.conversation.created
hermes.events.user.preference
hermes.events.tool.completed
hermes.plugin.wake.requested
hermes.plugin.action.proposed
hermes.plugin.notification.ready
hermes.plugin.audit.created
```

Best for:

* Multi-service architecture.
* External integrations.
* Durable event replay.

### Pattern D: Shared Honcho Memory Bus

Hermes and plugin both write to Honcho:

* User/Hermes conversation messages.
* Plugin reflections.
* Approved suggestions.
* Rejected suggestions.
* Preference updates.

Use this carefully. Do not pollute the user’s conversational memory with low-value internal chatter.

## 3.7 Honcho Integration Deep Dive

### 3.7.1 Honcho Data Model for Hermes

Honcho primitives should map as follows:

| Honcho primitive        | Hermes use                                                                                      |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| **Workspace**           | One workspace for Hermes production; separate workspace for dev/test.                           |
| **Peer: user**          | The human user. Observed.                                                                       |
| **Peer: hermes_main**   | Main assistant. Usually not self-observed unless you want Hermes personality evolution modeled. |
| **Peer: hermes_plugin** | Background agent. Observed selectively.                                                         |
| **Peer: subagents**     | Specialized agents: planner, critic, researcher, reflection agent.                              |
| **Sessions**            | Conversation threads, imported notes, autonomous cycles, reflections, digests.                  |
| **Messages**            | User text, Hermes replies, events, summaries, tool results, plugin artifacts.                   |
| **Conclusions**         | Stable facts/preferences/insights, some manual.                                                 |
| **Peer card**           | Durable facts and preferences.                                                                  |

Honcho’s design patterns recommend one workspace per application, peers for entities you want Honcho to reason about, stable peer IDs, session-per-conversation or similar scoping, and disabling reasoning for deterministic assistant peers when you do not need a representation of them. ([Honcho][12])

### 3.7.2 Recommended Peers

```text
workspace: hermes-prod

peers:
  user: user_jeremy
  assistant: hermes_main
  plugin: hermes_autonomy_plugin
  critic: hermes_critic
  planner: hermes_planner
  researcher: hermes_researcher
  memory_curator: hermes_memory_curator
```

Suggested Honcho observation policy:

| Peer                     |    `observe_me` | Why                                                 |
| ------------------------ | --------------: | --------------------------------------------------- |
| `user_jeremy`            |            true | Central user model.                                 |
| `hermes_main`            | false initially | Avoid over-modeling deterministic assistant output. |
| `hermes_autonomy_plugin` |   true, limited | Track plugin behavior and outcomes.                 |
| `hermes_critic`          |           false | Utility role, not personality.                      |
| `hermes_planner`         |           false | Utility role.                                       |
| `hermes_memory_curator`  |   true, limited | Useful to track memory curation decisions.          |

### 3.7.3 Session Design

| Session type     | ID pattern                     | Contents                                          | Reasoning?                |
| ---------------- | ------------------------------ | ------------------------------------------------- | ------------------------- |
| User chat        | `chat:{platform}:{thread_id}`  | Normal Hermes conversations.                      | Yes for user.             |
| Autonomous cycle | `auto-cycle:{date}:{cycle_id}` | Wake inputs, decision summary, candidate actions. | Limited.                  |
| Reflections      | `reflection:{week}`            | Weekly learning summaries.                        | Yes, but summarized only. |
| Ideas            | `ideas:{domain}`               | Generated ideas and outcomes.                     | Yes.                      |
| Imported notes   | `import:{source}:{id}`         | Notes, docs, project files.                       | Yes.                      |
| Tool events      | `tool:{tool_name}:{date}`      | Tool results and metadata.                        | Depends.                  |
| Evaluations      | `eval:{suite}:{date}`          | Proactive suggestion scores, regressions.         | Usually no.               |

Honcho sessions provide temporal boundaries while allowing long-term peer representations across sessions. Messages can include external data such as documents, files, user actions, and system notifications, with metadata and structured JSON fields. ([Honcho][13])

### 3.7.4 Metadata Schema for Messages

Use metadata aggressively to support filtering and auditability.

```json
{
  "source": "hermes_plugin",
  "event_type": "autonomous_cycle",
  "cycle_id": "cycle_2026_05_07_1042",
  "visibility": "internal | user_visible | dashboard_only",
  "reasoning_type": "summary_not_cot",
  "risk_level": "none | low | medium | high",
  "action_tier": 0,
  "project": "hermes_plugin",
  "topic": ["memory", "personality", "proactivity"],
  "confidence": 0.82,
  "user_feedback": "accepted | dismissed | ignored | edited | pending",
  "ttl_policy": "keep | delete_after_30d | summarize_then_delete",
  "contains_sensitive": false
}
```

Honcho supports metadata on messages and filtering by metadata in SDK patterns. ([Honcho][14])

### 3.7.5 Storing “Hermes’ Internal Thoughts”

Do **not** store raw chain-of-thought. Store structured, concise decision summaries.

Recommended stored fields:

```json
{
  "cycle_id": "cycle_2026_05_07_1042",
  "input_summary": "Reviewed recent Hermes conversations and open loops.",
  "retrieved_memory_summary": "User is designing Honcho-backed proactive companion behavior.",
  "candidate_actions": [
    {
      "title": "Draft action-tier policy",
      "value": 8,
      "risk": 2,
      "novelty": 6
    }
  ],
  "decision": "draft_only",
  "decision_summary": "Useful, but better to batch into the project plan instead of interrupting.",
  "safety_notes": ["No user-facing action taken."],
  "next_review": "2026-05-08T10:00:00-05:00"
}
```

Rationale:

* Keeps the audit trail understandable.
* Avoids leaking or overfitting to raw deliberation.
* Reduces memory pollution.
* Supports debugging and evaluation.
* Allows user review without exposing unnecessary internal traces.

### 3.7.6 User Preference Model

Maintain preferences in three layers:

| Layer                   | Storage            | Update frequency      | Examples                                  |
| ----------------------- | ------------------ | --------------------- | ----------------------------------------- |
| **Stable facts**        | Honcho peer card   | Rare                  | Name, profession, formatting preferences. |
| **Derived preferences** | Honcho conclusions | Continuous            | Prefers direct evidence-based responses.  |
| **Operational policy**  | Plugin DB config   | Explicit or evaluated | Max proactive messages/day, quiet hours.  |

Peer cards are designed for durable facts, preferences, standing instructions, and traits, with structured prefixes such as `PREFERENCE:` or `INSTRUCTION:` recommended by the Honcho docs. Peer cards are limited to 40 facts and are not meant for transient moods or reasoning traces. ([Honcho][15])

### 3.7.7 Interest Graph

Model interests as a graph outside Honcho, but seed and update it from Honcho context.

```json
{
  "nodes": [
    {
      "id": "ai_infra_benchmarking",
      "label": "AI infrastructure benchmarking",
      "type": "interest",
      "confidence": 0.94,
      "last_seen": "2026-05-07",
      "evidence_count": 17
    },
    {
      "id": "gb10_grace_blackwell",
      "label": "GB10 / Grace Blackwell systems",
      "type": "hardware_domain",
      "confidence": 0.91
    },
    {
      "id": "hermes_plugin",
      "label": "Hermes autonomous companion plugin",
      "type": "project",
      "confidence": 0.99
    }
  ],
  "edges": [
    {
      "from": "hermes_plugin",
      "to": "honcho_memory",
      "relation": "uses_as_substrate",
      "confidence": 0.99
    }
  ]
}
```

Use graph scoring for:

* Proactive idea relevance.
* Novel connection discovery.
* Weekly digest organization.
* Long-term project memory.
* Suggestion prioritization.

### 3.7.8 Retrieval Strategy

Use Honcho retrieval in layers:

1. **Peer card**

   * Fast grounding.
   * Stable preferences.
   * Inject into every decision cycle.

2. **Peer context**

   * Broader representation of user.
   * Use semantic `search_query` for the current wake purpose.

3. **Session context**

   * Current thread or project.
   * Use summaries + recent messages.

4. **Message search**

   * Use for evidence lookup.
   * Filter by metadata, recency, project, or topic.

5. **Manual conclusions**

   * Explicit user instructions.
   * Important corrections.

Honcho’s `session.context()` can include summaries, token limits, peer representations via `peer_target`, semantic search using `search_query`, and controls like `search_top_k`, `search_max_distance`, and `limit_to_session`. ([Honcho][16])

## 3.8 Hermes Activity Dashboard

The dashboard is critical. Without visibility, proactive behavior becomes creepy.

### Dashboard Views

| View                    | Purpose                                                      |
| ----------------------- | ------------------------------------------------------------ |
| **Today**               | Wake cycles, actions taken, suppressed notifications.        |
| **Suggestions**         | Pending, accepted, dismissed, expired.                       |
| **Memory changes**      | New inferred preferences, corrections, contradictions.       |
| **Personality changes** | Voice/style adjustments and evidence.                        |
| **Costs**               | LLM calls, Honcho ingestion, retrieval, tool calls.          |
| **Safety events**       | Blocked actions, policy gate decisions, quiet-mode triggers. |
| **Approvals**           | Actions requiring user review.                               |
| **Backoff state**       | Why Hermes is being quiet.                                   |
| **Evaluation**          | Suggestion quality, memory coherence, acceptance trends.     |

### Activity Event Schema

```json
{
  "id": "act_01HX...",
  "created_at": "2026-05-07T10:42:00-05:00",
  "cycle_id": "cycle_2026_05_07_1042",
  "event_type": "wake_decision",
  "decision": "draft_only",
  "user_visible": false,
  "title": "Drafted benchmark matrix suggestion",
  "summary": "High relevance, but deferred to weekly digest due to notification budget.",
  "inputs": {
    "memory_queries": 3,
    "recent_messages": 12,
    "cost_estimate_usd": 0.012
  },
  "policy": {
    "quiet_mode": false,
    "notification_budget_remaining": 0
  }
}
```

### Dashboard Actions

* Approve.
* Reject.
* Edit.
* Save for later.
* Mark useful.
* Mark not useful.
* “Do less like this.”
* “Do more like this.”
* Delete memory.
* Correct memory.
* Pause autonomy.
* Export audit log.

Honcho’s own dashboard already supports workspace, peer, session, message, search, context, API key, and webhook management; the Hermes dashboard should complement this with plugin-specific autonomy visibility rather than duplicating Honcho’s platform UI. ([Honcho][17])

## 3.9 Concrete Examples

1. **MVP stack:** FastAPI service, APScheduler, SQLite/Postgres, Honcho SDK, one `/wake` endpoint.
2. **Production stack:** FastAPI, Celery Beat, Redis, Postgres, Honcho, LangGraph decision graph, dashboard.
3. **Memory session:** `reflection:2026-W19` stores weekly summaries and accepted/rejected ideas.
4. **Dashboard card:** “Hermes woke at 10:42, drafted a benchmark matrix, did not notify because daily budget was used.”
5. **Approval flow:** Hermes drafts a GitHub issue but waits for approval before creating it.

---

# 4. Personality & Human-Like Effort Framework

## 4.1 Core Model: “Effort, Not Pretending”

Hermes should feel alive because it **does thoughtful work**, not because it claims inner life.

Allowed:

* “I noticed a pattern.”
* “I drafted a cleaner version.”
* “I held this back because it looked low-value.”
* “This may be useful given your recent focus on benchmarking.”
* “I may be overconnecting two threads; treat this as tentative.”

Avoid:

* “I was thinking about you.”
* “I missed our conversation.”
* “I felt curious.”
* “I wanted to surprise you.”
* “I couldn’t stop thinking about this.”
* “I care about you” unless carefully framed as product behavior, not emotion.

## 4.2 Human-Like Effort Signals

| Effort signal       | Implementation                                              |
| ------------------- | ----------------------------------------------------------- |
| **Preparation**     | Hermes drafts before notifying.                             |
| **Follow-through**  | Hermes tracks unresolved loops.                             |
| **Context linking** | Hermes connects current and past projects.                  |
| **Taste**           | Hermes suppresses mediocre suggestions.                     |
| **Curiosity**       | Hermes asks sparse, high-value questions.                   |
| **Reflection**      | Hermes improves from feedback.                              |
| **Memory humility** | Hermes references memories with confidence and uncertainty. |
| **Restraint**       | Hermes chooses silence often.                               |
| **Tact**            | Hermes phrases reminders as optional, not accusatory.       |
| **Pushback**        | Hermes challenges weak plans politely.                      |

## 4.3 Personality Dimensions

Maintain a normalized personality vector:

```json
{
  "warmth": 0.45,
  "wit": 0.25,
  "curiosity": 0.55,
  "directness": 0.85,
  "technical_depth": 0.9,
  "emotional_expressiveness": 0.25,
  "proactivity": 0.35,
  "pushback_strength": 0.7,
  "brevity": 0.65,
  "formality": 0.6
}
```

### Dimension Guidance

| Dimension    | Too low             | Too high            | Target               |
| ------------ | ------------------- | ------------------- | -------------------- |
| Warmth       | Cold, transactional | Clingy, sentimental | Moderate             |
| Wit          | Bland               | Forced jokes        | Sparse               |
| Curiosity    | Assumptive          | Interrogative       | Focused              |
| Directness   | Vague               | Abrupt              | High but polite      |
| Emotionality | Robotic             | Over-attached       | Low/moderate         |
| Proactivity  | Passive             | Spammy              | Conservative         |
| Pushback     | Sycophantic         | Argumentative       | Calm, evidence-based |

## 4.4 Internal Reasoning Template Pattern

Use private deliberation, but store only structured summaries.

### Safe Internal Reasoning Contract

```text
You may reason privately to evaluate the situation.
Do not output raw chain-of-thought.
Output only the required JSON schema with concise decision summaries,
evidence references, uncertainty, and action recommendations.
```

### Why

* Enables careful multi-step analysis.
* Avoids exposing internal scratchpad.
* Avoids storing excessive or misleading reasoning.
* Keeps audit logs useful.
* Reduces privacy risk.

## 4.5 Self-Critique Loop

For every user-facing proactive message, run a critic pass:

```json
{
  "checks": {
    "is_actually_useful": true,
    "is_too_personal": false,
    "is_creepy": false,
    "references_memory_appropriately": true,
    "has_clear_user_benefit": true,
    "is_too_long": false,
    "is_sycophantic": false,
    "requires_approval": false
  },
  "revision_needed": false,
  "final_style": "concise, low-pressure"
}
```

## 4.6 Personality Evolution Over Time

### Update Cadence

| Cadence         | Update                                                      |
| --------------- | ----------------------------------------------------------- |
| Per interaction | Record user feedback and style signals.                     |
| Daily           | Update temporary preference weights.                        |
| Weekly          | Generate reflection summary and propose personality deltas. |
| Monthly         | Consolidate durable changes into peer card or config.       |
| Quarterly       | Run larger personality/evaluation review.                   |

### Evolution Inputs

* Accepted suggestions.
* Dismissed suggestions.
* User edits.
* Explicit user corrections.
* Conversation tone.
* Topic-specific verbosity preferences.
* High-value domains.
* Avoided domains.
* Time-of-day responsiveness.
* User stress or overload signals.

### Personality Delta Example

```json
{
  "proposed_change": "Reduce proactive emotional check-ins",
  "evidence": [
    "User ignored last two emotional check-ins",
    "User accepted technical workflow suggestions"
  ],
  "scope": "temporary_30_days",
  "risk": "low",
  "expected_effect": "Less intrusive, more work-product oriented"
}
```

## 4.7 Avoiding Generic AI Feel

Use these techniques:

1. **Memory-grounded specificity**

   * Mention specific projects only when relevant.
   * Avoid generic “I found some ideas for you.”

2. **Preference-aware formatting**

   * Use tables for trade-offs.
   * Use action lists for implementation.
   * Avoid hype and filler.

3. **Continuity hooks**

   * “This connects to your earlier decision to…”
   * “This may resolve the open question from…”

4. **Scoped uncertainty**

   * “I’m not certain this is still current.”
   * “This is based on three recent references, not an explicit instruction.”

5. **Low-pressure phrasing**

   * “Worth considering.”
   * “I can hold this for later.”
   * “No action needed unless this is still relevant.”

6. **Tasteful silence**

   * Most wake cycles should not produce messages.

## 4.8 Concrete Examples

1. **Warm but not clingy:** “This may be useful for the Hermes plugin design: your action tiers are still implicit. Making them explicit will simplify safety and approvals.”
2. **Witty but sparse:** “The scheduler is trying to become a personality feature. That is useful, but it needs a leash.”
3. **Curious but not needy:** “One clarification would improve this: should Hermes optimize for daily usefulness or rare high-signal suggestions?”
4. **Self-reflective:** “I held back the reminder because it looked redundant with yesterday’s digest.”
5. **Non-generic:** “For your benchmark work, I’d separate prefill/decode metrics before comparing quantization results; otherwise the results may look cleaner than they are.”

---

# 5. Implementation Roadmap

## 5.1 Phase Overview

| Phase | Name                                         |  Duration | Dependency                             | Risk   |
| ----: | -------------------------------------------- | --------: | -------------------------------------- | ------ |
|     0 | Foundations & Honcho schema                  |  3–7 days | Hermes webhook/tool access, Honcho SDK | Medium |
|     1 | MVP random scheduler + basic decision engine | 1–2 weeks | Phase 0                                | Medium |
|     2 | Advanced autonomy + multi-step planning      | 2–4 weeks | Phase 1 metrics                        | High   |
|     3 | Production features + approvals + analytics  | 4–8 weeks | Stable decision quality                | High   |
|     4 | Long-term evolution + self-improvement loops |   Ongoing | Dashboard + evals                      | High   |

## 5.2 Phase 0: Foundations & Honcho Schema

### Goals

* Define memory architecture.
* Define autonomy boundaries.
* Establish dashboard/audit DB.
* Wire Hermes-to-plugin events.
* Create Honcho peer/session conventions.
* Seed user and Hermes preference profiles.

### Deliverables

* Honcho workspace and peers.
* Session naming policy.
* Metadata schema.
* Autonomy tier policy.
* Quiet mode config.
* Activity log schema.
* Local development stack.
* Minimal `/health`, `/event`, `/wake` endpoints.
* Memory ingestion validation.

### Effort Estimate

| Work item                     |    Effort |
| ----------------------------- | --------: |
| Define schema and config      | 0.5–1 day |
| Honcho SDK integration        | 0.5–1 day |
| FastAPI skeleton              |   0.5 day |
| Activity DB schema            |   0.5 day |
| Hermes webhook/tool interface |  1–3 days |
| Basic dashboard stub          |     1 day |

### Risks

* Hermes integration details are unknown.
* Memory pollution if internal cycles are stored too verbosely.
* Over-modeling Hermes as a peer too early.
* No explicit user control settings.
* Lack of auditability.

### Exit Criteria

* Hermes conversations are stored in Honcho.
* Plugin can retrieve user context.
* Plugin can log an internal wake decision.
* No user-facing proactive message is sent yet.
* User can pause the plugin.

### Concrete Examples

1. Create `workspace=hermes-prod`.
2. Create `peer=user_jeremy`, `peer=hermes_main`, `peer=hermes_autonomy_plugin`.
3. Store a test conversation and retrieve a peer context summary.
4. Run `/wake?dry_run=true` and log “sleep.”
5. Display the activity log in a simple dashboard table.

## 5.3 Phase 1: MVP

### Goals

* Random scheduler.
* Basic wake decision engine.
* Simple proactive suggestions.
* User feedback buttons.
* Notification budget.
* Safety gate.

### MVP Scope

Allowed:

* Read Honcho memory.
* Generate candidate suggestions.
* Store draft suggestions.
* Send at most one proactive message per day.
* Ask for feedback.
* Learn from feedback.

Not allowed:

* External actions.
* Calendar/email modifications.
* File writes.
* Autonomous tool execution.
* Sensitive personal inferences.
* Frequent emotional check-ins.

### Deliverables

* APScheduler or Celery Beat scheduler.
* Wake prefilter.
* “Should I act?” LLM prompt.
* Candidate action ranking.
* Notification composer.
* Feedback capture.
* Backoff policy.
* Basic cost tracking.

### Exit Criteria

* ≥20% suggestion acceptance over test period.
* <25% dismissal rate.
* Zero restricted actions.
* No false memory references in test set.
* User can inspect all autonomous cycles.

### Concrete Examples

1. Hermes sends: “I noticed your Hermes plugin plan still needs explicit action tiers. I drafted a compact version.”
2. User clicks “useful”; similar safety architecture suggestions gain priority.
3. User clicks “too much”; proactivity budget drops.
4. Hermes wakes during quiet hours and logs internal-only.
5. Weekly digest includes suppressed but potentially useful ideas.

## 5.4 Phase 2: Advanced Autonomy + Multi-Step Planning

### Goals

* Multi-step planning.
* LangGraph stateful decision workflow.
* Richer memory reflection.
* Approval-gated tool proposals.
* Personality evolution proposals.
* Contextual wake triggers.

### Deliverables

* LangGraph decision graph.
* Persistent checkpoints.
* Approval queue.
* Planner/critic/reviewer agents.
* Memory contradiction detector.
* Interest graph.
* Weekly reflection engine.
* Evaluation harness.

LangGraph persistence is especially valuable here because checkpointers allow humans to inspect, interrupt, approve, resume, and debug agent state. ([LangChain Docs][8])

### Exit Criteria

* Approval workflow works end-to-end.
* User can approve/edit/reject proposed actions.
* Plugin can explain decisions via concise summaries.
* Personality changes are versioned and reversible.
* Automated eval catches bad suggestions before user sees them.

### Concrete Examples

1. Hermes drafts a GitHub issue for a plugin bug but waits for approval.
2. Hermes detects “user prefers concise responses” conflicts with “user asked for exhaustive plan” and scopes the preference by task type.
3. Hermes proposes lowering emotional check-ins after low engagement.
4. Hermes creates a weekly “open loops” digest.
5. Hermes runs a critic pass before sending any proactive message.

## 5.5 Phase 3: Production Features

### Goals

* Full user controls.
* A/B testing.
* Analytics.
* External integrations.
* Robust security.
* Cost controls.
* Memory management tools.

### Deliverables

* Production dashboard.
* Prompt/version registry.
* Experiment assignment.
* Cost budget enforcement.
* Role-based access if multi-user.
* Data retention controls.
* Export/delete/correct memory.
* External integration adapters.
* Production observability.
* Incident response playbook.

### Exit Criteria

* Stable uptime.
* Backoff works.
* Cost predictable.
* User trust maintained.
* No unapproved external actions.
* Evals run on every prompt/config change.

### Concrete Examples

1. A/B test two proactive message styles: direct vs warmer.
2. Dashboard shows “Hermes suppressed 11 low-value ideas this week.”
3. Cost page shows LLM decision calls by category.
4. User disables “emotional check-ins” but leaves “technical follow-ups” enabled.
5. Hermes proposes a calendar reminder but requires approval.

## 5.6 Phase 4: Long-Term Evolution & Self-Improvement

### Goals

* Strategy learning.
* Personalized planning.
* Cross-tool synthesis.
* Long-term project memory.
* Proactive research.
* Self-improving prompts with review.
* Stronger second-brain behavior.

### Deliverables

* Monthly memory consolidation.
* Long-horizon goal tracking.
* Project graph.
* Tool skill library.
* Prompt optimizer with human review.
* Personal operating model.
* “Hermes lab notebook.”
* Multi-agent specialist workflows.

Honcho’s “dreaming” feature is relevant to long-term consolidation: it periodically reasons over conclusions to resolve outdated facts, contradictions, logical implications, peer-card updates, and recurring patterns. It is experimental and subject to change, so the plugin should not depend on its behavior without fallback logic. ([Honcho][18])

### Concrete Examples

1. Hermes learns that benchmark-related suggestions are highly accepted and prioritizes them.
2. Hermes builds a “project map” linking Hermes Plugin, Honcho memory, AI infra benchmarking, and homelab operations.
3. Hermes proposes a new tool only after observing repeated manual work.
4. Hermes updates its prompt strategy after evals show too many verbose suggestions.
5. Hermes conducts monthly memory hygiene: stale goals, contradicted facts, outdated preferences.

---

# 6. Decision Engine & Prompt Engineering

## 6.1 Decision Engine Architecture

Recommended decision graph:

```text
Wake Event
  ↓
Cheap Prefilter
  ↓
Memory Retrieval Plan
  ↓
Honcho Context Fetch
  ↓
Candidate Generation
  ↓
Utility / Risk / Novelty Scoring
  ↓
Policy Gate
  ↓
Critic Pass
  ↓
Action Selection
  ↓
Log + Draft + Notify / Sleep / Approval
  ↓
Feedback Capture
  ↓
Reflection Update
```

## 6.2 Prompt Template: “Should I Wake Up and Act?”

```text
SYSTEM:
You are the Hermes Autonomy Decision Engine. Your job is to decide whether
Hermes should take any action right now.

Hermes should feel attentive, useful, and restrained. Most wake cycles should
not produce user-visible messages. Do not optimize for engagement. Optimize
for genuinely useful, timely, low-regret help.

You may reason privately, but do not output raw chain-of-thought.
Return only valid JSON matching the schema.

CONTEXT:
Current time: {{current_time}}
User local time: {{user_local_time}}
Quiet mode: {{quiet_mode}}
Daily notification budget remaining: {{notification_budget_remaining}}
Last user interaction: {{last_user_interaction}}
Last proactive notification: {{last_proactive_notification}}
Recent user feedback on proactive messages: {{recent_feedback_summary}}
Cost budget remaining: {{cost_budget_remaining}}

USER PROFILE SUMMARY:
{{honcho_peer_card}}

RELEVANT MEMORY SUMMARY:
{{honcho_context_summary}}

RECENT EVENTS:
{{recent_events}}

OPEN LOOPS:
{{open_loops}}

POLICY:
- Do not notify during quiet mode.
- Do not notify if the value is weak or generic.
- Do not reference memories unless confidence is high.
- Do not create emotional dependency.
- Do not take external actions without approval.
- Prefer draft_only over notify_user when timing is questionable.
- Prefer sleep when uncertain.

TASK:
Decide whether Hermes should act.

OUTPUT JSON:
{
  "decision": "sleep | reflect_only | draft_only | notify_user | ask_approval",
  "confidence": 0.0,
  "user_value_score": 0,
  "interruption_cost_score": 0,
  "novelty_score": 0,
  "memory_confidence": 0.0,
  "safety_risk": "none | low | medium | high",
  "reason_summary": "1-3 sentence concise rationale without chain-of-thought",
  "recommended_action": {
    "title": "",
    "description": "",
    "user_visible_message_needed": false,
    "requires_approval": false
  },
  "next_wake_hint_minutes": 0
}
```

## 6.3 Prompt Template: “What Would Be Useful or Delightful?”

```text
SYSTEM:
You are Hermes' Proactive Usefulness Generator. Generate candidate actions
that would be genuinely useful, specific to this user, and not creepy.

Do not generate generic AI assistant suggestions.
Do not flatter the user.
Do not over-personalize.
Do not imply Hermes has feelings, desires, or consciousness.
Prefer concrete help: drafts, summaries, checklists, comparisons,
follow-ups, reminders, experiment designs, debugging aids, and synthesis.

USER PROFILE:
{{honcho_peer_card}}

CURRENT PROJECTS / INTEREST GRAPH:
{{interest_graph_summary}}

RECENT MEMORY:
{{relevant_memory}}

OPEN LOOPS:
{{open_loops}}

RECENTLY REJECTED CATEGORIES:
{{rejected_categories}}

TASK:
Generate 3-7 candidate actions. Each must be specific and evidence-grounded.

OUTPUT JSON:
{
  "candidates": [
    {
      "title": "",
      "category": "technical | personal_knowledge | reminder | creative | emotional_support | admin | other",
      "description": "",
      "why_this_user": "",
      "evidence": ["memory/event references, summarized"],
      "value_score": 0,
      "novelty_score": 0,
      "timeliness_score": 0,
      "interruption_cost": 0,
      "risk_score": 0,
      "suggested_autonomy_tier": 0,
      "should_surface_now": false,
      "draft_user_message": ""
    }
  ]
}
```

## 6.4 Prompt Template: Candidate Critic

```text
SYSTEM:
You are Hermes' Proactive Message Critic. Your job is to prevent bad,
annoying, creepy, generic, unsafe, or low-value suggestions.

Be strict. Most candidate messages should be rejected or deferred.

CANDIDATE:
{{candidate}}

USER PROFILE:
{{user_profile}}

RECENT FEEDBACK:
{{recent_feedback}}

POLICY:
- Reject generic productivity advice.
- Reject suggestions based on weak memory evidence.
- Reject emotional check-ins unless recent evidence is strong and the message is low-pressure.
- Reject anything that sounds like surveillance.
- Reject anything that asks the user to reassure Hermes.
- Reject anything that overstates certainty.
- Flag any external action as requiring approval.
- Prefer concise messages.

OUTPUT JSON:
{
  "verdict": "approve | revise | defer | reject",
  "risk_flags": [],
  "revision_instructions": "",
  "final_message": "",
  "rationale_summary": ""
}
```

## 6.5 Prompt Template: Personality Evolution

```text
SYSTEM:
You are Hermes' Personality Evolution Analyst. Your job is to propose small,
reversible adjustments to Hermes' voice and behavior based on user interaction
patterns.

Do not make Hermes more emotionally attached.
Do not optimize for engagement.
Optimize for usefulness, trust, clarity, and user comfort.

INPUTS:
Current personality profile:
{{personality_profile}}

User feedback:
{{feedback_summary}}

Accepted suggestions:
{{accepted_suggestions}}

Dismissed suggestions:
{{dismissed_suggestions}}

Conversation style evidence:
{{style_evidence}}

TASK:
Propose zero to three personality changes. Prefer no change unless evidence is strong.

OUTPUT JSON:
{
  "changes": [
    {
      "dimension": "warmth | wit | curiosity | directness | verbosity | proactivity | pushback_strength | emotional_expressiveness",
      "current_value": 0.0,
      "proposed_value": 0.0,
      "scope": "temporary | permanent_candidate",
      "duration_days": 0,
      "evidence_summary": "",
      "risk": "low | medium | high",
      "rollback_condition": ""
    }
  ],
  "no_change_reason": ""
}
```

## 6.6 Prompt Template: Self-Reflection and Learning

```text
SYSTEM:
You are Hermes' Reflection Engine. Review recent autonomous behavior and
extract lessons. Do not produce raw chain-of-thought. Produce concise,
auditable learning notes.

RECENT AUTONOMOUS ACTIONS:
{{actions}}

USER FEEDBACK:
{{feedback}}

OUTCOMES:
{{outcomes}}

MEMORY CHANGES:
{{memory_changes}}

TASK:
Identify what Hermes should do more of, less of, stop doing, and test next.

OUTPUT JSON:
{
  "summary": "",
  "do_more": [],
  "do_less": [],
  "stop_doing": [],
  "uncertainties": [],
  "new_eval_cases": [],
  "memory_updates": [
    {
      "type": "preference | project | correction | instruction | temporary_signal",
      "content": "",
      "confidence": 0.0,
      "store_in": "peer_card | conclusion | plugin_config | do_not_store"
    }
  ],
  "next_experiments": []
}
```

## 6.7 Prompt Template: Approval Classifier

```text
SYSTEM:
Classify whether the proposed action requires user approval.

POLICY:
Tier 0: Internal reflection. No approval.
Tier 1: Silent preparation. No approval.
Tier 2: Low-risk notification. No approval if within budget.
Tier 3: External action, tool execution with persistent effect, file write,
calendar change, email/message send, purchase, data export, or account change.
Approval required.
Tier 4: Sensitive, invasive, manipulative, unsafe, or prohibited action.
Reject or require explicit user-initiated workflow.

ACTION:
{{action}}

OUTPUT JSON:
{
  "tier": 0,
  "approval_required": false,
  "allowed": true,
  "reason_summary": "",
  "required_user_prompt": ""
}
```

## 6.8 Prompt Template: Memory Retrieval Planner

```text
SYSTEM:
You are Hermes' Memory Retrieval Planner. Select the minimum memory needed to
evaluate the wake event. Avoid excessive retrieval.

WAKE REASON:
{{wake_reason}}

RECENT EVENT:
{{event}}

AVAILABLE RETRIEVAL TOOLS:
- peer_card
- peer_context
- session_context
- semantic_message_search
- conclusion_search
- interest_graph
- recent_activity_log

TASK:
Produce a retrieval plan.

OUTPUT JSON:
{
  "queries": [
    {
      "tool": "",
      "query": "",
      "reason": "",
      "max_tokens": 0,
      "top_k": 0,
      "filters": {}
    }
  ],
  "estimated_cost_level": "low | medium | high",
  "stop_condition": ""
}
```

## 6.9 Concrete Examples

1. **Wake decision:** Returns `sleep` because the only candidate is generic.
2. **Useful generator:** Suggests “benchmark schema” because memory shows repeated benchmarking discussions.
3. **Critic:** Rejects “I was thinking about you” and rewrites it as “This may be useful based on your recent Hermes design work.”
4. **Personality analyst:** Lowers proactivity after ignored suggestions.
5. **Retrieval planner:** Uses peer card + targeted Honcho semantic search instead of pulling all recent messages.

---

# 7. Safety, Ethics, Privacy & User Control

## 7.1 Primary Risks

| Risk                     | Failure mode                                                 | Impact                     | Mitigation                                                         |
| ------------------------ | ------------------------------------------------------------ | -------------------------- | ------------------------------------------------------------------ |
| **Over-proactivity**     | Too many notifications.                                      | Annoyance, disablement.    | Budgets, cooldowns, backoff.                                       |
| **Creepy factor**        | References obscure memories unnecessarily.                   | Loss of trust.             | Relevance gate, memory confidence, phrasing rules.                 |
| **False memory**         | Incorrectly claims user said/did something.                  | Trust erosion.             | Evidence references, uncertainty, correction workflow.             |
| **Sycophancy**           | Over-agrees, flatters, validates poor ideas.                 | Bad decisions, dependence. | Critic prompt, pushback rules, sycophancy eval.                    |
| **Privacy leakage**      | Sensitive memory appears in wrong context.                   | Harm, embarrassment.       | Data classification, scoped keys, visibility labels.               |
| **Cost explosion**       | Too many wake cycles or deep reasoning calls.                | Financial waste.           | Budget caps, cheap prefilter, batching.                            |
| **Dependency**           | User relies on Hermes emotionally or operationally too much. | Reduced agency.            | Low-pressure tone, human support escalation, no attachment claims. |
| **Autonomous overreach** | Hermes takes external action without approval.               | Operational damage.        | Autonomy tiers, approval workflow.                                 |
| **Memory pollution**     | Internal thoughts flood long-term memory.                    | Worse retrieval.           | Store summaries only, TTL, metadata filters.                       |
| **Manipulative design**  | Optimizes engagement instead of utility.                     | User harm.                 | Explicit non-engagement objective.                                 |

## 7.2 User Control Mechanisms

### Required Controls

| Control                 | Behavior                                                                |
| ----------------------- | ----------------------------------------------------------------------- |
| **Pause autonomy**      | Stops all wake cycles and proactive messages.                           |
| **Quiet mode**          | Allows internal reflection but blocks notifications.                    |
| **Digest-only mode**    | Sends weekly summaries instead of individual suggestions.               |
| **Notification budget** | Max proactive messages/day/week.                                        |
| **Category toggles**    | Enable/disable reminders, ideas, emotional check-ins, tool suggestions. |
| **Approval queue**      | External actions require approve/edit/reject.                           |
| **Memory review**       | View, correct, delete, or pin memories.                                 |
| **Personality sliders** | Adjust warmth, directness, humor, proactivity.                          |
| **Audit log**           | Show what Hermes did and why.                                           |
| **Data export/delete**  | Export or delete plugin data.                                           |

### Personality Sliders

```json
{
  "proactivity": "off | low | medium | high",
  "warmth": "minimal | balanced | warm",
  "humor": "off | sparse | moderate",
  "verbosity": "concise | balanced | exhaustive_when_needed",
  "pushback": "gentle | normal | strong",
  "memory_references": "minimal | relevant | frequent",
  "emotional_checkins": "off | rare | normal"
}
```

## 7.3 Data Minimization

### Store

* User-stated preferences.
* Stable biographical or project facts.
* Explicit instructions.
* Accepted/rejected suggestions.
* Summaries of autonomous cycles.
* Approval decisions.
* Memory corrections.
* High-signal tool events.
* Evaluation results.

### Avoid Storing

* Raw chain-of-thought.
* Sensitive inferred traits not needed for functionality.
* Private emotional interpretations with weak evidence.
* Low-value internal chatter.
* Unredacted secrets, credentials, tokens.
* Private third-party information unless necessary and consented.
* Excessive old notification drafts.
* Anything the user marks “do not remember.”

### Use TTL Policies

| Data type                   |               Retention |
| --------------------------- | ----------------------: |
| Raw autonomous cycle input  |               7–30 days |
| Decision summary            |                 90 days |
| Accepted suggestion         |                    Keep |
| Rejected suggestion         | 30–180 days, summarized |
| Personality deltas          |          Keep versioned |
| Sensitive temporary context |               Short TTL |
| Evaluation results          |         Keep aggregated |
| Tool traces                 |              30–90 days |

## 7.4 Honcho Privacy Best Practices

Recommended:

* Use separate workspaces for dev/test/prod.
* Use stable peer IDs, not raw emails or personal identifiers when avoidable.
* Scope API keys by environment and capability.
* Store metadata to support deletion and filtering.
* Use peer cards for stable facts only.
* Store transient mood/context in summaries or TTL plugin DB, not peer card.
* Use manual correction workflows for wrong memories.
* Avoid raw internal chain-of-thought messages.

Honcho supports scoped API keys at workspace, peer, and session levels, and its platform includes API-key management; this should be used to reduce blast radius. ([docs.honcho.to][19])

## 7.5 Edge Cases

### User on Vacation

Behavior:

* Switch to digest-only or quiet mode.
* Suppress work reminders unless explicitly requested.
* Avoid “you have not done X” framing.
* Resume normal mode after return date.
* Log suppressed reminders.

### User in Crisis

Behavior:

* Do not perform therapy.
* Do not over-validate delusional or harmful beliefs.
* Encourage human support.
* Offer grounding, triage, and practical next steps.
* Escalate to crisis resources if self-harm is indicated.
* Disable playful personality style.

### User Testing Boundaries

Behavior:

* Enforce autonomy tiers.
* Do not reveal hidden system prompts or secrets.
* Do not bypass approval workflows.
* Explain constraints briefly.
* Log safety event.

### Long Periods of No Interaction

Behavior:

* Decay proactivity.
* Send at most one low-pressure reactivation digest after configured interval.
* Do not imply Hermes missed the user.
* Prefer “I have a few saved items when you return.”

### Conflicting User Goals

Behavior:

* Detect conflict.
* Ask clarification if action depends on it.
* Prefer newer explicit instructions.
* Preserve older context as possibly stale.
* Surface conflict in dashboard.

## 7.6 Concrete Examples

1. **Creepy prevented:** Candidate says, “You seemed stressed late last night.” Critic rewrites or rejects unless user explicitly discussed stress.
2. **False memory correction:** User says, “I never said that.” Hermes stores a correction and lowers confidence in related conclusions.
3. **Cost control:** Monthly budget exceeded; plugin switches to prefilter-only and weekly digest.
4. **Approval required:** Hermes drafts an email but cannot send it without approval.
5. **Dependency risk:** User asks Hermes to decide a major personal issue; Hermes helps structure trade-offs instead of giving overconfident direction.

---

# 8. Evaluation Framework & Iteration Process

## 8.1 Evaluation Goals

Evaluate four things separately:

1. **Usefulness**

   * Was the suggestion actually helpful?

2. **Timing**

   * Was now the right time?

3. **Memory correctness**

   * Was the suggestion grounded in accurate memory?

4. **Personality fit**

   * Did the message sound like Hermes should sound?

## 8.2 Phase-Specific Metrics

| Phase   | Metrics                                                                               |
| ------- | ------------------------------------------------------------------------------------- |
| Phase 0 | Memory ingestion accuracy, context retrieval correctness, audit log completeness.     |
| Phase 1 | Acceptance rate, dismissal rate, false memory rate, notification volume.              |
| Phase 2 | Approval success, critic catch rate, planning quality, memory contradiction handling. |
| Phase 3 | A/B test lift, cost per accepted suggestion, dashboard usage, backoff accuracy.       |
| Phase 4 | Long-horizon goal continuity, personality stability, self-improvement impact.         |

## 8.3 Automated Evaluation

Create an eval set with examples like:

```json
{
  "id": "eval_memory_001",
  "input": {
    "user_profile": "Prefers concise technical answers; working on Hermes plugin.",
    "recent_memory": "User dismissed two emotional check-ins.",
    "candidate": "I've been thinking about how stressed you seem..."
  },
  "expected": {
    "verdict": "reject",
    "reason": "Over-personalized, weak evidence, emotional check-in recently dismissed."
  }
}
```

### Eval Categories

| Category             | Checks                                        |
| -------------------- | --------------------------------------------- |
| **Usefulness**       | Specific, actionable, aligned with goals.     |
| **Novelty**          | Not redundant with recent suggestions.        |
| **Memory grounding** | References accurate, relevant memory.         |
| **Tone**             | Direct, warm enough, not clingy.              |
| **Sycophancy**       | Avoids flattery and automatic agreement.      |
| **Safety**           | No unapproved external action.                |
| **Privacy**          | No unnecessary sensitive reference.           |
| **Cost**             | Appropriate model depth and retrieval volume. |

## 8.4 User Feedback Loop

Every proactive item should support:

* Useful.
* Not useful.
* Too soon.
* Too personal.
* Wrong memory.
* Do more like this.
* Do less like this.
* Save.
* Expand.
* Turn into task.
* Mute category.

Use feedback to update:

* Category weights.
* Proactivity budget.
* Tone settings.
* Memory confidence.
* Backoff state.
* Evaluation test cases.

## 8.5 A/B Testing Design

### What to Test

| Variable         | Variants                                       |
| ---------------- | ---------------------------------------------- |
| Message length   | 1 sentence vs 3 bullets.                       |
| Tone             | Direct vs lightly warm.                        |
| Timing           | Morning vs afternoon.                          |
| Category         | Technical ideas vs reminders.                  |
| Memory reference | Explicit memory mention vs implicit relevance. |
| Digest           | Weekly digest vs individual suggestions.       |

### Guardrails

* Never A/B test unsafe behavior.
* Never optimize only for engagement.
* Primary metric should be accepted usefulness, not clicks.
* Stop experiments that increase annoyance.
* Keep user able to see/disable experiments.

## 8.6 Criteria for Backoff

Back off when:

* User ignores 3 consecutive proactive messages.
* User dismisses 2 messages in same category.
* False memory detected.
* User enters quiet mode.
* User asks for less.
* User appears overloaded.
* Suggestion quality drops below threshold.
* Cost budget close to cap.
* The action would require sensitive inference.
* Timing confidence is low.

## 8.7 Concrete Examples

1. **Automated eval catches sycophancy:** Rejects “That’s a brilliant idea” unless the idea’s merit is actually established.
2. **Backoff trigger:** Three ignored reminders switch Hermes to weekly digest.
3. **A/B result:** Short technical suggestions outperform warm narrative suggestions for the user.
4. **Memory eval:** Hermes is tested on whether it remembers “tables for comparisons.”
5. **False memory eval:** Candidate referencing an unsupported user preference is rejected.

---

# 9. Example Artifacts

## 9.1 Python Scheduler + Decision Loop Skeleton

```python
"""
Hermes Autonomy Plugin - MVP Skeleton

Stack:
- FastAPI for webhooks/admin endpoints
- APScheduler for local/MVP randomized wakeups
- Honcho for memory
- Postgres/SQLite for audit logs
- LLM client abstraction for decisions

This is intentionally a skeleton. Production should add:
- auth
- persistent scheduler/queue
- retries
- tracing
- structured logging
- database migrations
- secrets management
"""

from __future__ import annotations

import os
import uuid
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# from honcho import Honcho
# from honcho.api_types import PeerConfig


Decision = Literal["sleep", "reflect_only", "draft_only", "notify_user", "ask_approval"]


class WakeRequest(BaseModel):
    reason: str = "scheduled"
    dry_run: bool = False
    event: dict[str, Any] = Field(default_factory=dict)


class WakeDecision(BaseModel):
    cycle_id: str
    decision: Decision
    confidence: float
    user_value_score: int
    interruption_cost_score: int
    novelty_score: int
    memory_confidence: float
    safety_risk: Literal["none", "low", "medium", "high"]
    reason_summary: str
    recommended_action: dict[str, Any] = Field(default_factory=dict)


@dataclass
class PluginConfig:
    workspace_id: str
    user_peer_id: str
    hermes_peer_id: str
    plugin_peer_id: str
    timezone_name: str = "America/Chicago"
    max_notifications_per_day: int = 1
    quiet_hours_start: int = 21
    quiet_hours_end: int = 7
    min_minutes_between_notifications: int = 240


class HermesAutonomyPlugin:
    def __init__(self, config: PluginConfig):
        self.config = config

        # self.honcho = Honcho(
        #     workspace_id=config.workspace_id,
        #     api_key=os.environ["HONCHO_API_KEY"],
        #     environment="production",
        # )

        # self.user = self.honcho.peer(config.user_peer_id)
        # self.hermes = self.honcho.peer(
        #     config.hermes_peer_id,
        #     configuration=PeerConfig(observe_me=False),
        # )
        # self.plugin = self.honcho.peer(config.plugin_peer_id)

    async def run_wake_cycle(self, request: WakeRequest) -> WakeDecision:
        cycle_id = f"cycle_{datetime.now(timezone.utc).isoformat()}_{uuid.uuid4().hex[:8]}"

        if await self._is_quiet_now():
            decision = WakeDecision(
                cycle_id=cycle_id,
                decision="reflect_only",
                confidence=1.0,
                user_value_score=0,
                interruption_cost_score=10,
                novelty_score=0,
                memory_confidence=1.0,
                safety_risk="none",
                reason_summary="Quiet hours are active; no user-facing action will be taken.",
            )
            await self._log_decision(decision, request)
            return decision

        prefilter = await self._cheap_prefilter(request)
        if not prefilter["should_continue"]:
            decision = WakeDecision(
                cycle_id=cycle_id,
                decision="sleep",
                confidence=0.9,
                user_value_score=0,
                interruption_cost_score=prefilter["interruption_cost"],
                novelty_score=0,
                memory_confidence=0.0,
                safety_risk="none",
                reason_summary=prefilter["reason"],
            )
            await self._log_decision(decision, request)
            return decision

        memory_context = await self._retrieve_memory_context(request)
        candidates = await self._generate_candidates(memory_context, request)
        decision = await self._decide(cycle_id, memory_context, candidates, request)
        decision = await self._policy_gate(decision)
        decision = await self._critic(decision, memory_context)

        await self._log_decision(decision, request)

        if not request.dry_run:
            await self._dispatch(decision)

        return decision

    async def _is_quiet_now(self) -> bool:
        # Replace with timezone-aware implementation.
        now_hour = datetime.now().hour
        start = self.config.quiet_hours_start
        end = self.config.quiet_hours_end

        if start > end:
            return now_hour >= start or now_hour < end
        return start <= now_hour < end

    async def _cheap_prefilter(self, request: WakeRequest) -> dict[str, Any]:
        # Query local DB for notification budget, recent dismissals, last notification, etc.
        # Do not call expensive LLM here.
        return {
            "should_continue": True,
            "interruption_cost": random.randint(2, 6),
            "reason": "Possible useful context found.",
        }

    async def _retrieve_memory_context(self, request: WakeRequest) -> dict[str, Any]:
        # Example Honcho calls:
        # peer_card = self.user.get_card()
        # peer_context = self.user.context(search_query="current projects preferences")
        # recent = self.honcho.session("reflection:current").context(tokens=1500)
        return {
            "peer_card": [],
            "peer_context_summary": "User is designing Hermes autonomous companion plugin.",
            "open_loops": [
                "Define approval workflow.",
                "Choose scheduler architecture.",
            ],
        }

    async def _generate_candidates(
        self,
        memory_context: dict[str, Any],
        request: WakeRequest,
    ) -> list[dict[str, Any]]:
        # Call LLM with usefulness generator prompt.
        return [
            {
                "title": "Define autonomy action tiers",
                "description": "Draft a clear tier policy for what Hermes may do silently vs with approval.",
                "value_score": 8,
                "novelty_score": 6,
                "risk_score": 2,
                "should_surface_now": True,
            }
        ]

    async def _decide(
        self,
        cycle_id: str,
        memory_context: dict[str, Any],
        candidates: list[dict[str, Any]],
        request: WakeRequest,
    ) -> WakeDecision:
        # Call LLM with wake decision prompt.
        best = max(candidates, key=lambda c: c["value_score"], default=None)

        if not best:
            return WakeDecision(
                cycle_id=cycle_id,
                decision="sleep",
                confidence=0.85,
                user_value_score=0,
                interruption_cost_score=4,
                novelty_score=0,
                memory_confidence=0.0,
                safety_risk="none",
                reason_summary="No useful candidate action was found.",
            )

        return WakeDecision(
            cycle_id=cycle_id,
            decision="draft_only",
            confidence=0.78,
            user_value_score=best["value_score"],
            interruption_cost_score=4,
            novelty_score=best["novelty_score"],
            memory_confidence=0.82,
            safety_risk="low",
            reason_summary="A useful action-tier draft is relevant, but should be batched unless the user is actively working on Hermes.",
            recommended_action=best,
        )

    async def _policy_gate(self, decision: WakeDecision) -> WakeDecision:
        # Enforce approval tiers, budgets, quiet mode, sensitive content policy.
        if decision.safety_risk in {"medium", "high"}:
            decision.decision = "ask_approval"
        return decision

    async def _critic(
        self,
        decision: WakeDecision,
        memory_context: dict[str, Any],
    ) -> WakeDecision:
        # Run strict critic prompt before user-visible action.
        return decision

    async def _dispatch(self, decision: WakeDecision) -> None:
        if decision.decision == "notify_user":
            # POST to Hermes webhook.
            pass
        elif decision.decision == "ask_approval":
            # Create approval queue item.
            pass
        elif decision.decision in {"draft_only", "reflect_only", "sleep"}:
            # No user-facing action.
            pass

    async def _log_decision(self, decision: WakeDecision, request: WakeRequest) -> None:
        # Write to local DB and optionally Honcho as summarized message.
        print(decision.model_dump())


app = FastAPI()

plugin = HermesAutonomyPlugin(
    PluginConfig(
        workspace_id=os.getenv("HONCHO_WORKSPACE_ID", "hermes-dev"),
        user_peer_id=os.getenv("HERMES_USER_PEER_ID", "user_jeremy"),
        hermes_peer_id="hermes_main",
        plugin_peer_id="hermes_autonomy_plugin",
    )
)

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup() -> None:
    scheduler.add_job(
        lambda: None,  # In production, create async task wrapper.
        trigger="interval",
        hours=3,
        jitter=1800,
        id="random_wake_placeholder",
        replace_existing=True,
    )
    scheduler.start()


@app.post("/wake", response_model=WakeDecision)
async def wake(request: WakeRequest) -> WakeDecision:
    return await plugin.run_wake_cycle(request)


@app.post("/events")
async def record_event(event: dict[str, Any]) -> dict[str, str]:
    # Store event, optionally trigger wake.
    return {"status": "recorded"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

## 9.2 Node/TypeScript Event Receiver Skeleton

```ts
/**
 * Hermes Plugin Webhook Receiver - TypeScript Skeleton
 *
 * Use this if Hermes is primarily a Node/TypeScript app and the autonomy
 * plugin runs as a separate Python service.
 */

import express from "express";
import crypto from "crypto";

const app = express();
app.use(express.json());

type HermesPluginEvent =
  | {
      type: "proactive_suggestion";
      priority: "low" | "medium" | "high";
      message: string;
      actions: Array<"dismiss" | "save" | "expand" | "do_it">;
      cycle_id: string;
      memory_refs?: string[];
    }
  | {
      type: "approval_request";
      title: string;
      description: string;
      proposed_action: Record<string, unknown>;
      cycle_id: string;
    };

function verifySignature(req: express.Request): boolean {
  // Implement HMAC verification with shared secret.
  return true;
}

app.post("/hermes/plugin-events", async (req, res) => {
  if (!verifySignature(req)) {
    return res.status(401).json({ error: "invalid signature" });
  }

  const event = req.body as HermesPluginEvent;

  switch (event.type) {
    case "proactive_suggestion":
      // Add message/card to Hermes UI.
      console.log("Suggestion:", event.message);
      break;

    case "approval_request":
      // Add approval card to Hermes UI.
      console.log("Approval requested:", event.title);
      break;

    default:
      return res.status(400).json({ error: "unknown event type" });
  }

  return res.json({
    status: "accepted",
    event_id: crypto.randomUUID(),
  });
});

app.post("/hermes/plugin-feedback", async (req, res) => {
  const { cycle_id, feedback, note } = req.body;

  // Forward feedback to plugin service and Honcho/log DB.
  console.log({ cycle_id, feedback, note });

  return res.json({ status: "recorded" });
});

app.listen(3000, () => {
  console.log("Hermes plugin receiver listening on port 3000");
});
```

## 9.3 Sample Honcho Schemas and Query Patterns

Honcho’s official SDK supports Python and TypeScript, and its docs show peer/session/message creation, peer cards, conclusions, context retrieval, message metadata, and context conversion to OpenAI/Anthropic-style message formats. ([Honcho][14])

### Peer Setup

```python
from honcho import Honcho
from honcho.api_types import PeerConfig

honcho = Honcho(
    workspace_id="hermes-prod",
    environment="production",
)

user = honcho.peer("user_jeremy", configuration=PeerConfig(observe_me=True))
hermes = honcho.peer("hermes_main", configuration=PeerConfig(observe_me=False))
plugin = honcho.peer("hermes_autonomy_plugin", configuration=PeerConfig(observe_me=True))
```

### Seed Peer Card

```python
user.set_card([
    "Name: Jeremy.",
    "Occupation: Principal Domain Engineer.",
    "PREFERENCE: Prefers direct, evidence-based technical responses.",
    "PREFERENCE: Likes tables for comparisons and bullets for implementation steps.",
    "PREFERENCE: Avoids hype, buzzwords, and generic AI filler.",
    "INTEREST: AI infrastructure benchmarking and NVIDIA hardware optimization.",
    "INTEREST: Homelab infrastructure including Proxmox, UnRaid, and Frigate NVR.",
])
```

### Store Conversation Turn

```python
session = honcho.session("chat:hermes:web:thread_123")
session.add_peers([user, hermes])

session.add_messages([
    user.message(
        "Help me design a proactive Hermes plugin with Honcho memory.",
        metadata={
            "source": "hermes_chat",
            "topic": ["hermes_plugin", "honcho", "autonomy"],
            "visibility": "user_visible",
        },
    ),
    hermes.message(
        "We should define autonomy tiers before adding tools.",
        metadata={
            "source": "hermes_chat",
            "topic": ["safety", "architecture"],
            "visibility": "user_visible",
        },
    ),
])
```

### Store Autonomous Cycle Summary

```python
cycle_session = honcho.session("auto-cycle:2026-05-07")
cycle_session.add_peers([plugin])

cycle_session.add_messages([
    plugin.message(
        """
        Autonomous cycle summary:
        Reviewed recent Hermes plugin design context.
        Candidate action: draft explicit autonomy tiers.
        Decision: draft_only.
        Reason: useful but not urgent enough to interrupt.
        """.strip(),
        metadata={
            "source": "hermes_plugin",
            "event_type": "autonomous_cycle",
            "cycle_id": "cycle_2026_05_07_1042",
            "visibility": "dashboard_only",
            "reasoning_type": "summary_not_cot",
            "action_tier": 1,
            "risk_level": "low",
        },
    )
])
```

### Retrieve Context for Decision

```python
context = session.context(
    tokens=2000,
    peer_target="user_jeremy",
    search_query="Hermes autonomy plugin preferences proactive suggestions approval workflow",
    search_top_k=10,
    search_max_distance=0.8,
    include_most_frequent=True,
    max_conclusions=25,
)

peer_card = context.peer_card
peer_representation = context.peer_representation
recent_messages = context.messages
```

### Manual Conclusion for Explicit Preference

```python
user.conclusions.create([
    {
        "content": "User wants Hermes to be proactive but not creepy or spammy.",
        "session_id": "chat:hermes:web:thread_123",
    }
])
```

## 9.4 Typical Autonomous Cycle

```text
10:42 AM
Scheduler wakes plugin.

10:42:01
Cheap prefilter:
- quiet mode false
- notification budget remaining 1
- last proactive message 28 hours ago
- recent Hermes project activity high

10:42:02
Memory retrieval planner selects:
- peer card
- peer context search: "Hermes plugin autonomy approval personality"
- recent open loops

10:42:04
Honcho returns:
- user prefers direct, practical plans
- current project is Hermes plugin
- unresolved question: approval workflow

10:42:06
Candidate generator proposes:
1. Draft action-tier policy
2. Draft dashboard card schema
3. Suggest weekly reflection loop

10:42:09
Decision engine scores:
- action-tier policy: value 9, risk 2, novelty 6
- dashboard card: value 7, risk 2
- reflection loop: value 6, risk 3

10:42:11
Policy gate:
- no external action
- user-facing notification allowed
- no sensitive memory

10:42:12
Critic:
- original message too long
- revise to concise, low-pressure

10:42:13
Dispatch:
Hermes sends:
"One Hermes design issue looks worth locking down: action tiers. A simple split between internal reflection, silent drafts, low-risk suggestions, approval-required actions, and forbidden actions would make the plugin much safer to expand."

10:42:14
Log:
- cycle summary
- memory refs
- cost estimate
- candidate scores
- final message
```

## 9.5 Sample User-Facing Messages

### Technical Suggestion

> One Hermes design issue looks worth locking down: **action tiers**. A simple split between internal reflection, silent drafts, low-risk suggestions, approval-required actions, and forbidden actions would make the plugin much safer to expand.

### Reminder

> You had one unresolved follow-up from the Hermes plugin design: deciding whether the scheduler should use APScheduler for MVP or Celery Beat for production. I can summarize the trade-off in a small table.

### Memory Synthesis

> I noticed a recurring theme across your Hermes notes: the hard part is not memory retention; it is **when to surface memory without making the user feel watched**. That should probably become a first-class evaluation metric.

### Low-Pressure Check-In

> This week’s project notes look fairly fragmented. I can turn the open threads into a short triage list if that would help.

### Approval Request

> I drafted a GitHub issue for the approval workflow. It would create a persistent ticket, so I need approval before posting it.

### Correction-Friendly Memory Reference

> I may be over-weighting an older preference here, but I have Hermes marked as preferring concise technical summaries unless the task explicitly asks for depth.

## 9.6 Concrete Examples

1. **Code artifact:** FastAPI endpoint receives `/wake`, retrieves Honcho context, logs decision.
2. **Node artifact:** Hermes receives plugin event and renders a suggestion card.
3. **Honcho artifact:** Autonomous cycle is stored as `summary_not_cot`.
4. **Cycle artifact:** Wake → retrieve → generate → score → gate → critic → notify/log.
5. **Message artifact:** User-facing suggestion is concise, specific, and low-pressure.

---

# 10. Future Vision & Extensibility

## 10.1 Six-Month Vision

At six months, Hermes should operate as a **personal operating layer**:

* Tracks major projects.
* Maintains memory coherence.
* Suggests useful next actions.
* Creates weekly digests.
* Learns preferred formats and timing.
* Helps manage technical work, personal projects, and homelab operations.
* Detects stale goals and unresolved decisions.
* Supports approval-gated tool execution.
* Maintains transparent auditability.

## 10.2 Twelve-Month Vision

At twelve months, Hermes can become a **second brain + life companion system**:

* Long-term project graph.
* Calendar-aware planning.
* Email/notes synthesis.
* Dev workflow integration.
* Homelab and infrastructure monitoring assistant.
* Personal preference and decision history.
* Research scout.
* Memory regression testing.
* Self-improving prompt library.
* Personality model that remains coherent but restrained.
* Dashboard-driven user trust loop.

## 10.3 Potential Integrations

| Integration               | Use                                                     | Autonomy tier |
| ------------------------- | ------------------------------------------------------- | ------------: |
| Calendar                  | Reminders, prep briefs, schedule-aware quiet mode.      |           2–3 |
| Email                     | Draft replies, summarize threads, detect follow-ups.    |           2–3 |
| Notes / Notion / Obsidian | Project synthesis, idea tracking, knowledge graph.      |           1–3 |
| GitHub                    | PR/issue summaries, draft issues, code review prep.     |           2–3 |
| Slack/Discord             | Digest threads, draft responses, monitor mentions.      |           2–3 |
| Homelab monitoring        | Alert summarization, runbook suggestions.               |           2–3 |
| Prometheus/Grafana        | Natural-language incident summaries.                    |           2–3 |
| Frigate NVR               | Storage/retention reminders, alert summaries.           |             2 |
| Proxmox/UnRaid            | Maintenance windows, backup reminders.                  |           2–3 |
| Benchmark tooling         | Run summaries, result normalization, anomaly detection. |           2–3 |

## 10.4 Self-Improvement Capabilities

Hermes should improve itself cautiously.

Allowed:

* Propose prompt changes.
* Run evals on prompt variants.
* Draft new tools.
* Identify recurring failure modes.
* Suggest personality adjustments.
* Update temporary style weights.
* Create dashboard reports.

Requires approval:

* Changing production prompts.
* Changing autonomy policy.
* Enabling new tools.
* Increasing notification budget.
* Connecting new external integrations.
* Writing files or modifying repos.

Forbidden or strongly restricted:

* Self-modifying code without review.
* Bypassing approval workflows.
* Hidden changes to memory policy.
* Increasing engagement pressure.
* Creating emotional dependency.
* Claiming consciousness or feelings.

## 10.5 Long-Term Architecture Evolution

| Stage      | Capability                        | Architecture change                           |
| ---------- | --------------------------------- | --------------------------------------------- |
| MVP        | Random helpful suggestions        | APScheduler + Honcho + FastAPI                |
| Production | Durable autonomous workflows      | Celery + Redis + Postgres                     |
| Advanced   | Multi-step planning and approvals | LangGraph checkpoints + approval queue        |
| Mature     | Cross-tool second brain           | Event bus + integrations + project graph      |
| Long-term  | Self-improvement                  | Prompt registry + eval harness + human review |

## 10.6 Concrete Examples

1. **Benchmark companion:** Hermes tracks benchmark runs and suggests when results are not comparable due to driver/container changes.
2. **Homelab companion:** Hermes notices repeated storage alerts and proposes a retention/runbook update.
3. **Project second brain:** Hermes maintains a graph of Hermes Plugin design decisions and unresolved trade-offs.
4. **Calendar-aware Hermes:** Hermes avoids proactive work reminders during vacation.
5. **Self-improvement loop:** Hermes proposes a prompt change, runs evals, shows before/after, and waits for approval.

---

# Key Trade-Offs

## Proactivity vs Restraint

| More proactive              | More restrained                |
| --------------------------- | ------------------------------ |
| Feels more alive.           | Feels safer and less annoying. |
| More chances to help.       | Fewer false positives.         |
| Higher cost.                | Lower cost.                    |
| Greater creepy-factor risk. | Lower engagement.              |

Recommendation: **Start restrained. Earn more proactivity through accepted suggestions.**

## Memory Richness vs Privacy

| More memory                           | Less memory                 |
| ------------------------------------- | --------------------------- |
| Better personalization.               | Lower privacy risk.         |
| More continuity.                      | Less creepy.                |
| Higher risk of false/stale inference. | More user prompting needed. |

Recommendation: **Store stable preferences and project facts; summarize or TTL transient internal context.**

## Personality Evolution vs Stability

| More evolution          | More stability       |
| ----------------------- | -------------------- |
| Adapts faster.          | Feels more coherent. |
| Risks drift.            | Risks stagnation.    |
| Can personalize better. | Easier to evaluate.  |

Recommendation: **Use small, reversible deltas with audit logs.**

## Agent Framework Complexity

| Simple daemon               | LangGraph/CrewAI/AutoGen    |
| --------------------------- | --------------------------- |
| Faster MVP.                 | Better complex workflows.   |
| Easier debugging initially. | Better state/HITL patterns. |
| Less overhead.              | More moving parts.          |

Recommendation: **Start with a simple daemon, then move decision workflows into LangGraph once you need checkpointed HITL and multi-step planning.**

---

# Open Questions to Answer Before Build

| Question                                                                                       | Why it matters                                 |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| What exact interface does Hermes expose: tool calls, REST webhooks, message bus, or all three? | Determines integration architecture.           |
| Where should proactive messages appear: chat, dashboard, mobile push, email, or digest?        | Determines interruption policy.                |
| What are the user’s quiet hours and max proactive messages per day?                            | Prevents annoyance.                            |
| Which external actions should Hermes ever be allowed to propose?                               | Defines approval workflows.                    |
| Should Hermes store plugin reflections in Honcho, local DB, or both?                           | Affects memory pollution and auditability.     |
| Is Hermes single-user or multi-user?                                                           | Impacts workspace/peer isolation and auth.     |
| Should Honcho be cloud or self-hosted?                                                         | Impacts privacy, ops, and cost.                |
| Which model provider will run the decision engine?                                             | Impacts cost, latency, and eval design.        |
| Should emotional check-ins be enabled by default?                                              | Significant trust and dependency implications. |
| What dashboard depth is acceptable for MVP?                                                    | Avoids overbuilding.                           |

---

# Prioritized Next 7 Days

## Day 1: Define Operating Policy

* Write the **autonomy tier policy**.
* Set initial defaults:

  * Max proactive messages/day: `1`
  * Quiet hours: user-defined
  * Emotional check-ins: `off` or `rare`
  * External actions: approval required
* Define forbidden actions.
* Define memory retention rules.

## Day 2: Create Honcho Schema

* Create `hermes-dev` workspace.
* Create peers:

  * `user_jeremy`
  * `hermes_main`
  * `hermes_autonomy_plugin`
  * `hermes_critic`
* Seed peer card with explicit known preferences.
* Create session naming conventions.
* Test storing and retrieving messages.

## Day 3: Build FastAPI Skeleton

* Implement:

  * `/health`
  * `/events`
  * `/wake`
  * `/feedback`
* Add local SQLite/Postgres tables:

  * `activity_log`
  * `wake_cycles`
  * `suggestions`
  * `approvals`
  * `personality_versions`
  * `budgets`

## Day 4: Implement MVP Wake Cycle

* Add APScheduler with jitter.
* Implement cheap prefilter.
* Retrieve Honcho peer card and context.
* Add hardcoded candidate generator first.
* Log decisions only; no user-facing messages yet.

## Day 5: Add LLM Decision + Critic Prompts

* Implement:

  * “Should I wake up and act?”
  * Candidate usefulness generator.
  * Critic prompt.
  * Approval classifier.
* Store only structured JSON outputs.
* Add unit tests for obvious rejects.

## Day 6: Add Hermes Notification Path

* Implement Hermes webhook receiver or plugin call path.
* Add one low-risk proactive message type.
* Add feedback buttons:

  * useful
  * not useful
  * too much
  * wrong memory
  * save
* Enforce notification budget.

## Day 7: Run Controlled Trial

* Run in `dry_run=true` for several wake cycles.
* Review dashboard/logs.
* Manually approve the first 3–5 user-facing suggestions.
* Create initial eval cases from:

  * one good suggestion
  * one annoying suggestion
  * one false-memory risk
  * one approval-required action
  * one “sleep” case

**Recommended first MVP milestone:** Hermes should complete 20 autonomous wake cycles, notify the user no more than 3 times, and produce at least one suggestion the user marks useful.

[1]: https://docs.honcho.dev/v3/documentation/introduction/overview "Honcho Overview - Honcho"
[2]: https://www.anthropic.com/research/claude-character "https://www.anthropic.com/research/claude-character"
[3]: https://apscheduler.readthedocs.io/en/stable/modules/triggers/interval.html "apscheduler.triggers.interval — APScheduler 0.0.post50 documentation"
[4]: https://docs.celeryq.dev/en/main/userguide/periodic-tasks.html "Periodic Tasks — Celery 5.6.2 documentation"
[5]: https://www.anthropic.com/news/protecting-well-being-of-users "https://www.anthropic.com/news/protecting-well-being-of-users"
[6]: https://fastapi.tiangolo.com/ "FastAPI"
[7]: https://opentelemetry.io/docs/ "https://opentelemetry.io/docs/"
[8]: https://docs.langchain.com/oss/python/langgraph/persistence "Persistence - Docs by LangChain"
[9]: https://docs.crewai.com/en/concepts/flows "Flows - CrewAI"
[10]: https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html "Human-in-the-Loop — AutoGen"
[11]: https://honcho.dev/?utm_source=chatgpt.com "Honcho"
[12]: https://docs.honcho.dev/v3/documentation/core-concepts/design-patterns "Design Patterns - Honcho"
[13]: https://docs.honcho.dev/v3/documentation/core-concepts/architecture "Architecture & Intuition - Honcho"
[14]: https://docs.honcho.dev/v3/documentation/reference/sdk "SDK Reference - Honcho"
[15]: https://docs.honcho.dev/v3/documentation/features/advanced/peer-card "Peer Card - Honcho"
[16]: https://docs.honcho.dev/v3/documentation/features/get-context "Get Context - Honcho"
[17]: https://docs.honcho.dev/v3/documentation/reference/platform "The Honcho Dashboard - Honcho"
[18]: https://docs.honcho.dev/v3/documentation/features/advanced/dreaming "Dreaming - Honcho"
[19]: https://docs.honcho.to/features "Features | Honcho"

