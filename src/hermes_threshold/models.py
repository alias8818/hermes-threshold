from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Decision = Literal["sleep", "reflect_only", "draft_only", "notify_user", "ask_approval"]
SafetyRisk = Literal["none", "low", "medium", "high"]
FeedbackRating = Literal["useful", "not_useful", "too_much", "wrong_memory", "save"]


class WakeRequest(BaseModel):
    reason: str = "scheduled"
    dry_run: bool = False
    event: dict[str, Any] = Field(default_factory=dict)


class WakeDecision(BaseModel):
    cycle_id: str
    decision: Decision
    confidence: float = Field(ge=0.0, le=1.0)
    user_value_score: int = Field(ge=0, le=10)
    interruption_cost_score: int = Field(ge=0, le=10)
    novelty_score: int = Field(ge=0, le=10)
    memory_confidence: float = Field(ge=0.0, le=1.0)
    safety_risk: SafetyRisk
    reason_summary: str
    recommended_action: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EventRequest(BaseModel):
    event_type: str = Field(min_length=1)
    source: str = "hermes"
    payload: dict[str, Any] = Field(default_factory=dict)
    trigger_wake: bool = False


class FeedbackRequest(BaseModel):
    cycle_id: str = Field(min_length=1)
    suggestion_id: str | None = None
    rating: FeedbackRating
    note: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    db_ready: bool
    scheduler_enabled: bool


class EventResponse(BaseModel):
    status: Literal["recorded"]
    event_id: str
    wake_decision: WakeDecision | None = None


class FeedbackResponse(BaseModel):
    status: Literal["recorded"]
    feedback_id: str


class Suggestion(BaseModel):
    suggestion_id: str
    cycle_id: str
    created_at: datetime
    title: str
    description: str
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)


class SuggestionListResponse(BaseModel):
    suggestions: list[Suggestion]


class SuggestionReviewResponse(BaseModel):
    suggestion: Suggestion


class TrialSummaryResponse(BaseModel):
    counts: dict[str, int]
    drafted_suggestions: int
    approved_suggestions: int
    dismissed_suggestions: int
    useful_feedback: int
    annoyance_feedback: int
