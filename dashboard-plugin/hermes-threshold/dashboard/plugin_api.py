from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query


router = APIRouter()

DEFAULT_ENV_FILE = Path.home() / ".config" / "hermes-threshold" / "service.env"
DEFAULT_BASE_URL = "http://127.0.0.1:8789"


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            values[key] = value
    return values


def _settings() -> tuple[str, str | None]:
    env_file = Path(os.getenv("HERMES_THRESHOLD_ENV_FILE", str(DEFAULT_ENV_FILE))).expanduser()
    file_values = _read_env_file(env_file)
    base_url = (
        os.getenv("HERMES_THRESHOLD_URL")
        or file_values.get("HERMES_THRESHOLD_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")
    token = os.getenv("HERMES_THRESHOLD_API_TOKEN") or file_values.get("HERMES_THRESHOLD_API_TOKEN")
    return base_url, token


def _headers(token: str | None) -> dict[str, str]:
    if not token:
        return {}
    return {"authorization": f"Bearer {token}"}


async def _proxy_json(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> Any:
    base_url, token = _settings()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method,
                f"{base_url}{path}",
                headers=_headers(token),
                params=params,
                json=json,
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "threshold_unreachable", "message": str(exc)},
        ) from exc

    if response.status_code >= 400:
        detail: Any
        try:
            detail = response.json()
        except ValueError:
            detail = {"error": "threshold_error", "message": response.text}
        raise HTTPException(status_code=response.status_code, detail=detail)

    if not response.content:
        return {"ok": True}

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": "threshold_invalid_json"},
        ) from exc


@router.get("/health")
async def health() -> dict[str, Any]:
    service = await _proxy_json("GET", "/health")
    return {"status": "ok", "service": service}


@router.get("/summary")
async def trial_summary() -> Any:
    return await _proxy_json("GET", "/trial-summary")


@router.get("/suggestions")
async def suggestions(
    status: str | None = Query(default="drafted"),
    limit: int = Query(default=20, ge=1, le=100),
) -> Any:
    params: dict[str, Any] = {"limit": limit}
    if status:
        params["status"] = status
    return await _proxy_json("GET", "/suggestions", params=params)


@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: str) -> Any:
    return await _proxy_json("POST", f"/suggestions/{suggestion_id}/approve")


@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(suggestion_id: str) -> Any:
    return await _proxy_json("POST", f"/suggestions/{suggestion_id}/dismiss")


@router.post("/suggestions/batch-dismiss")
async def batch_dismiss_suggestions(payload: dict[str, Any]) -> dict[str, Any]:
    suggestion_ids = payload.get("suggestion_ids")
    if not isinstance(suggestion_ids, list):
        raise HTTPException(
            status_code=400,
            detail={"error": "suggestion_ids_required"},
        )

    updated: list[Any] = []
    for suggestion_id in suggestion_ids:
        if not isinstance(suggestion_id, str) or not suggestion_id:
            continue
        updated.append(await _proxy_json("POST", f"/suggestions/{suggestion_id}/dismiss"))
    return {"updated": updated, "count": len(updated)}


@router.post("/feedback")
async def feedback(payload: dict[str, Any]) -> Any:
    return await _proxy_json("POST", "/feedback", json=payload)
