from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status

from hermes_threshold.auth import require_api_token
from hermes_threshold.config import Settings
from hermes_threshold.engine import ThresholdEngine
from hermes_threshold.models import (
    EventRequest,
    EventResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    SuggestionListResponse,
    SuggestionReviewResponse,
    TrialSummaryResponse,
    WakeDecision,
    WakeRequest,
)
from hermes_threshold.store import SQLiteStore


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    store = SQLiteStore(resolved_settings.db_path)
    engine = ThresholdEngine(resolved_settings, store)
    scheduler = AsyncIOScheduler()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        store.init_schema()
        if resolved_settings.scheduler_enabled:
            interval_seconds = (
                resolved_settings.scheduler_interval_seconds
                or resolved_settings.scheduler_interval_hours * 3600
            )
            scheduler.add_job(
                lambda: asyncio.create_task(
                    engine.run_wake_cycle(
                        WakeRequest(
                            reason="scheduled",
                            dry_run=True,
                            event={
                                "source": "scheduler",
                                "note": resolved_settings.scheduler_event_note,
                            },
                        )
                    )
                ),
                trigger="interval",
                seconds=interval_seconds,
                jitter=resolved_settings.scheduler_jitter_seconds,
                id="random_wake",
                replace_existing=True,
            )
            scheduler.start()
        try:
            yield
        finally:
            if scheduler.running:
                scheduler.shutdown(wait=False)

    app = FastAPI(
        title="Hermes Threshold",
        version="0.1.0",
        summary="Restrained wake-decision threshold service for Hermes.",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.store = store
    app.state.engine = engine
    app.state.scheduler = scheduler

    async def authenticated(
        authorization: str | None = Header(default=None),
        x_hermes_threshold_token: str | None = Header(default=None),
    ) -> None:
        return await require_api_token(
            resolved_settings,
            authorization=authorization,
            x_hermes_threshold_token=x_hermes_threshold_token,
        )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        store.init_schema()
        return HealthResponse(
            status="ok",
            service="hermes-threshold",
            db_ready=True,
            scheduler_enabled=resolved_settings.scheduler_enabled,
        )

    @app.post("/wake", response_model=WakeDecision, dependencies=[Depends(authenticated)])
    async def wake(request: WakeRequest) -> WakeDecision:
        return await engine.run_wake_cycle(request)

    @app.post("/events", response_model=EventResponse, dependencies=[Depends(authenticated)])
    async def record_event(request: EventRequest) -> EventResponse:
        event_id = store.record_activity(
            activity_type=request.event_type,
            source=request.source,
            payload=request.payload,
        )
        wake_decision = None
        if request.trigger_wake:
            wake_decision = await engine.run_wake_cycle(
                WakeRequest(
                    reason=f"event:{request.event_type}",
                    dry_run=True,
                    event=request.payload,
                )
            )
        return EventResponse(status="recorded", event_id=event_id, wake_decision=wake_decision)

    @app.post("/feedback", response_model=FeedbackResponse, dependencies=[Depends(authenticated)])
    async def record_feedback(request: FeedbackRequest) -> FeedbackResponse:
        feedback_id = store.record_feedback(request)
        return FeedbackResponse(status="recorded", feedback_id=feedback_id)

    @app.get(
        "/suggestions",
        response_model=SuggestionListResponse,
        dependencies=[Depends(authenticated)],
    )
    async def list_suggestions(
        status: str | None = Query(default="drafted"),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> SuggestionListResponse:
        return SuggestionListResponse(suggestions=store.list_suggestions(status, limit))

    @app.post(
        "/suggestions/{suggestion_id}/approve",
        response_model=SuggestionReviewResponse,
        dependencies=[Depends(authenticated)],
    )
    async def approve_suggestion(suggestion_id: str) -> SuggestionReviewResponse:
        suggestion = store.update_suggestion_status(suggestion_id, "approved")
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found.",
            )
        return SuggestionReviewResponse(suggestion=suggestion)

    @app.post(
        "/suggestions/{suggestion_id}/dismiss",
        response_model=SuggestionReviewResponse,
        dependencies=[Depends(authenticated)],
    )
    async def dismiss_suggestion(suggestion_id: str) -> SuggestionReviewResponse:
        suggestion = store.update_suggestion_status(suggestion_id, "dismissed")
        if suggestion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found.",
            )
        return SuggestionReviewResponse(suggestion=suggestion)

    @app.get(
        "/trial-summary",
        response_model=TrialSummaryResponse,
        dependencies=[Depends(authenticated)],
    )
    async def trial_summary() -> TrialSummaryResponse:
        summary = store.trial_summary()
        return TrialSummaryResponse(
            counts={
                key: summary[key]
                for key in [
                    "activity_log",
                    "wake_cycles",
                    "suggestions",
                    "approvals",
                    "feedback",
                    "personality_versions",
                    "budgets",
                ]
            },
            drafted_suggestions=summary["drafted_suggestions"],
            approved_suggestions=summary["approved_suggestions"],
            dismissed_suggestions=summary["dismissed_suggestions"],
            useful_feedback=summary["useful_feedback"],
            annoyance_feedback=summary["annoyance_feedback"],
        )

    return app


app = create_app()


def main() -> None:
    uvicorn.run("hermes_threshold.app:app", host="127.0.0.1", port=8789, reload=False)


if __name__ == "__main__":
    main()
