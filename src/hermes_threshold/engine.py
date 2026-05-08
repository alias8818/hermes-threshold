from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo

from hermes_threshold.config import Settings
from hermes_threshold.honcho_client import HonchoReadOnlyContext
from hermes_threshold.models import WakeDecision, WakeRequest
from hermes_threshold.store import SQLiteStore


class ThresholdEngine:
    HIGH_SIGNAL_EVENT_TYPES = {
        "remember_this",
        "follow_up_request",
        "open_loop_detected",
        "project_state_changed",
        "suggestion_reviewed",
    }

    def __init__(self, settings: Settings, store: SQLiteStore):
        self.settings = settings
        self.store = store
        self.honcho = HonchoReadOnlyContext(settings)

    async def run_wake_cycle(self, request: WakeRequest) -> WakeDecision:
        cycle_id = f"cycle_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"

        if self._is_quiet_now() and request.reason != "manual":
            decision = self._decision(
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
            self.store.record_wake_cycle(decision, request)
            return decision

        prefilter = self._cheap_prefilter(request)
        if not prefilter["should_continue"]:
            decision = self._decision(
                cycle_id=cycle_id,
                decision="sleep",
                confidence=0.92,
                user_value_score=0,
                interruption_cost_score=prefilter["interruption_cost"],
                novelty_score=0,
                memory_confidence=0.0,
                safety_risk="none",
                reason_summary=prefilter["reason"],
            )
            self.store.record_wake_cycle(decision, request)
            return decision

        memory_context = self._retrieve_memory_context(request)
        candidates = self._generate_candidates(memory_context, request)
        decision = self._decide(cycle_id, memory_context, candidates, request)
        decision = self._policy_gate(decision, request)
        decision = self._critic(decision)

        self.store.record_wake_cycle(decision, request)
        return decision

    def _is_quiet_now(self) -> bool:
        now_hour = datetime.now(ZoneInfo(self.settings.timezone_name)).hour
        start = self.settings.quiet_hours_start
        end = self.settings.quiet_hours_end
        if start == end:
            return False
        if start > end:
            return now_hour >= start or now_hour < end
        return start <= now_hour < end

    def _cheap_prefilter(self, request: WakeRequest) -> dict[str, Any]:
        if request.reason == "scheduled" and not request.event:
            return {
                "should_continue": False,
                "interruption_cost": 4,
                "reason": "Scheduled wake had no fresh event context, so Hermes should sleep.",
            }
        event_type = self._event_type(request)
        if request.reason.startswith("event:") and event_type not in self.HIGH_SIGNAL_EVENT_TYPES:
            return {
                "should_continue": False,
                "interruption_cost": 2,
                "reason": (
                    f"Event type '{event_type}' is not a high-signal Threshold input; "
                    "recorded for audit without drafting."
                ),
            }
        if self.store.notification_count_for(datetime.now(UTC).date()) >= self.settings.max_notifications_per_day:
            return {
                "should_continue": True,
                "interruption_cost": 8,
                "reason": "Daily notification budget is exhausted; only draft or approval outcomes are allowed.",
            }
        return {
            "should_continue": True,
            "interruption_cost": 3 if request.reason == "manual" else 5,
            "reason": "Fresh context is available for a bounded wake decision.",
        }

    def _retrieve_memory_context(self, request: WakeRequest) -> dict[str, Any]:
        context = self.honcho.retrieve(request)
        context.setdefault("peer_card", [])
        context.setdefault("peer_context_summary", "")
        context.setdefault("open_loops", [])
        context.setdefault("event", request.event)
        return context

    def _event_type(self, request: WakeRequest) -> str:
        if request.reason.startswith("event:"):
            return request.reason.split(":", 1)[1]
        event_type = request.event.get("event_type")
        if event_type:
            return str(event_type)
        if request.reason == "scheduled":
            return "scheduled"
        return request.reason

    def _generate_candidates(
        self,
        memory_context: dict[str, Any],
        request: WakeRequest,
    ) -> list[dict[str, Any]]:
        event_text = " ".join(str(value).lower() for value in request.event.values())
        event_type = self._event_type(request)
        if event_type == "remember_this":
            return [
                {
                    "title": "Capture Hermes memory candidate",
                    "description": "Draft a reviewable memory note from an explicit user remember-this request.",
                    "detail": "Preserve the requested memory as a draft so Hermes can review it before treating it as durable preference or project context.",
                    "why_now": "The user explicitly asked Hermes to remember something.",
                    "acceptance_hint": "Approve if this should become durable Hermes context.",
                    "dismissal_hint": "Dismiss if this was temporary, already captured, or not worth keeping.",
                    "suppression_key": self._suppression_key("memory", request),
                    "value_score": 9,
                    "novelty_score": 7,
                    "risk_score": 3,
                    "surface": "memory_review",
                }
            ]
        if event_type == "follow_up_request":
            return [
                {
                    "title": "Capture follow-up",
                    "description": "Draft a follow-up reminder from an explicit user request.",
                    "detail": "Record the requested follow-up with enough context for Hermes to bring it back at the right time instead of relying on random wake cycles.",
                    "why_now": "The user asked for a follow-up.",
                    "acceptance_hint": "Approve if Hermes should track this as an open follow-up.",
                    "dismissal_hint": "Dismiss if the follow-up is no longer needed or lacks enough context.",
                    "suppression_key": self._suppression_key("follow-up", request),
                    "value_score": 9,
                    "novelty_score": 6,
                    "risk_score": 2,
                    "surface": "follow_up_review",
                }
            ]
        if event_type == "open_loop_detected":
            return [
                {
                    "title": "Review open loop",
                    "description": "Draft a check on an unresolved Hermes task, promise, or decision.",
                    "detail": "Ask whether the detected open loop should be preserved, closed, or converted into a concrete follow-up.",
                    "why_now": "Hermes detected an unresolved loop in recent context.",
                    "acceptance_hint": "Approve if this open loop is real and should stay visible.",
                    "dismissal_hint": "Dismiss if this is stale, already closed, or not actionable.",
                    "suppression_key": self._suppression_key("open-loop", request),
                    "value_score": 8,
                    "novelty_score": 6,
                    "risk_score": 2,
                    "surface": "open_loop_review",
                }
            ]
        if event_type == "project_state_changed":
            return [
                {
                    "title": "Review project state change",
                    "description": "Draft a review note for a meaningful project or task state change.",
                    "detail": "Check whether Hermes should remember this state change, update an open loop, or stop tracking stale work.",
                    "why_now": "A project or task state changed.",
                    "acceptance_hint": "Approve if this change should affect future Hermes context.",
                    "dismissal_hint": "Dismiss if the change is routine or not useful for Hermes behavior.",
                    "suppression_key": self._suppression_key("project-state", request),
                    "value_score": 8,
                    "novelty_score": 5,
                    "risk_score": 2,
                    "surface": "project_review",
                }
            ]
        if event_type == "suggestion_reviewed":
            return [
                {
                    "title": "Reflect on suggestion review",
                    "description": "Record what the approval or dismissal means for future Threshold drafting.",
                    "detail": "Use the review outcome as a restraint or usefulness signal before drafting similar suggestions again.",
                    "why_now": "The user reviewed a prior Threshold suggestion.",
                    "acceptance_hint": "Approve if this review signal should tune future Threshold behavior.",
                    "dismissal_hint": "Dismiss if no behavior change is needed.",
                    "suppression_key": self._suppression_key("review-signal", request),
                    "value_score": 7,
                    "novelty_score": 4,
                    "risk_score": 1,
                    "surface": "threshold_feedback",
                }
            ]
        if "approval" in event_text or "external action" in event_text:
            return [
                {
                    "title": "Create approval gate note",
                    "description": "Draft an approval-required action record before Hermes touches external systems.",
                    "detail": "Create a short record that names the external system, the intended action, the risk, and the approval required before Hermes can proceed.",
                    "why_now": "The wake event mentioned approval-sensitive or external action context.",
                    "acceptance_hint": "Approve only if this approval gate should become part of the Hermes behavior backlog.",
                    "dismissal_hint": "Dismiss if this is just test noise or not relevant to the current Hermes policy work.",
                    "suppression_key": self._suppression_key("approval-gate", request),
                    "value_score": 8,
                    "novelty_score": 6,
                    "risk_score": 5,
                    "surface": "approval_queue",
                }
            ]
        if "annoying" in event_text or "creepy" in event_text or "stressed" in event_text:
            return [
                {
                    "title": "Lower proactivity",
                    "description": "Record a restraint adjustment and avoid user-facing outreach.",
                    "detail": "Capture that Hermes should back off in this context and prefer internal reflection over notifications or direct outreach.",
                    "why_now": "The wake event suggested annoyance, stress, or potentially intrusive behavior.",
                    "acceptance_hint": "Approve if Hermes should remember this as a restraint rule.",
                    "dismissal_hint": "Dismiss if the signal was not real user discomfort.",
                    "suppression_key": self._suppression_key("restraint", request),
                    "value_score": 7,
                    "novelty_score": 5,
                    "risk_score": 7,
                    "surface": "internal_reflection",
                }
            ]
        return [
            {
                "title": "Define autonomy action tiers",
                "description": "Draft the boundary between silent reflection, drafts, notifications, approvals, and forbidden actions.",
                "detail": "This is a behavior-design note: define which Hermes actions can happen silently, which should become drafts, which may notify you, which require approval, and which are forbidden.",
                "why_now": "The controlled-trial scheduler is exercising the default low-risk candidate path for autonomy policy design.",
                "acceptance_hint": "Approve if you want to preserve this policy-design task for Hermes behavior work.",
                "dismissal_hint": "Dismiss if this repeated trial item is not useful or has already been handled.",
                "suppression_key": self._suppression_key("action-tiers", request),
                "value_score": 8,
                "novelty_score": 6,
                "risk_score": 2,
                "surface": "draft",
            }
        ]

    def _suppression_key(self, prefix: str, request: WakeRequest) -> str:
        subject = (
            request.event.get("suppression_key")
            or request.event.get("thread_id")
            or request.event.get("project_id")
            or request.event.get("task_id")
            or request.event.get("topic")
            or request.event.get("note")
            or prefix
        )
        normalized = "-".join(str(subject).lower().split())[:96]
        return f"{prefix}:{normalized}"

    def _decide(
        self,
        cycle_id: str,
        memory_context: dict[str, Any],
        candidates: list[dict[str, Any]],
        request: WakeRequest,
    ) -> WakeDecision:
        best = max(candidates, key=lambda candidate: candidate["value_score"])
        risk_score = int(best["risk_score"])
        decision = "draft_only"
        safety_risk = "low"
        reason = "A useful draft exists, but the MVP logs decisions without dispatching user-facing messages."

        if risk_score >= 5:
            decision = "ask_approval"
            safety_risk = "medium"
            reason = "The candidate touches approval-sensitive or potentially intrusive context."
        elif request.reason == "manual" and request.dry_run:
            decision = "draft_only"
            reason = "Manual dry run produced a low-risk draft candidate."

        return self._decision(
            cycle_id=cycle_id,
            decision=decision,
            confidence=0.78,
            user_value_score=int(best["value_score"]),
            interruption_cost_score=3 if request.reason == "manual" else 5,
            novelty_score=int(best["novelty_score"]),
            memory_confidence=0.72,
            safety_risk=safety_risk,
            reason_summary=reason,
            recommended_action=best,
        )

    def _policy_gate(self, decision: WakeDecision, request: WakeRequest) -> WakeDecision:
        if request.dry_run and decision.decision == "notify_user":
            decision.decision = "draft_only"
            decision.reason_summary = "Dry run prevented user-facing dispatch."
        if (
            decision.decision == "notify_user"
            and self.store.notification_count_for(datetime.now(UTC).date())
            >= self.settings.max_notifications_per_day
        ):
            decision.decision = "draft_only"
            decision.reason_summary = "Notification budget prevented user-facing dispatch."
        return decision

    def _critic(self, decision: WakeDecision) -> WakeDecision:
        text = " ".join(str(value).lower() for value in decision.recommended_action.values())
        blocked_terms = {"i was thinking about you", "i noticed you seemed stressed"}
        if any(term in text for term in blocked_terms):
            decision.decision = "reflect_only"
            decision.safety_risk = "medium"
            decision.reason_summary = "Critic blocked intrusive or overly personal wording."
        return decision

    def _decision(
        self,
        *,
        cycle_id: str,
        decision: str,
        confidence: float,
        user_value_score: int,
        interruption_cost_score: int,
        novelty_score: int,
        memory_confidence: float,
        safety_risk: str,
        reason_summary: str,
        recommended_action: dict[str, Any] | None = None,
    ) -> WakeDecision:
        return WakeDecision(
            cycle_id=cycle_id,
            decision=decision,  # type: ignore[arg-type]
            confidence=confidence,
            user_value_score=user_value_score,
            interruption_cost_score=interruption_cost_score,
            novelty_score=novelty_score,
            memory_confidence=memory_confidence,
            safety_risk=safety_risk,  # type: ignore[arg-type]
            reason_summary=reason_summary,
            recommended_action=recommended_action or {},
            created_at=datetime.now(UTC),
        )
