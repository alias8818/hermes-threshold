from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from hermes_threshold.config import Settings
from hermes_threshold.engine import ThresholdEngine
from hermes_threshold.models import (
    EventRequest,
    EventResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
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
            scheduler.add_job(
                lambda: asyncio.create_task(
                    engine.run_wake_cycle(WakeRequest(reason="scheduled", dry_run=True))
                ),
                trigger="interval",
                hours=resolved_settings.scheduler_interval_hours,
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

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        store.init_schema()
        return HealthResponse(
            status="ok",
            service="hermes-threshold",
            db_ready=True,
            scheduler_enabled=resolved_settings.scheduler_enabled,
        )

    @app.post("/wake", response_model=WakeDecision)
    async def wake(request: WakeRequest) -> WakeDecision:
        return await engine.run_wake_cycle(request)

    @app.post("/events", response_model=EventResponse)
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

    @app.post("/feedback", response_model=FeedbackResponse)
    async def record_feedback(request: FeedbackRequest) -> FeedbackResponse:
        feedback_id = store.record_feedback(request)
        return FeedbackResponse(status="recorded", feedback_id=feedback_id)

    return app


app = create_app()


def main() -> None:
    uvicorn.run("hermes_threshold.app:app", host="127.0.0.1", port=8789, reload=False)


if __name__ == "__main__":
    main()
