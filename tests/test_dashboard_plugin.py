from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient


PLUGIN_PATH = (
    Path(__file__).resolve().parents[1]
    / "dashboard-plugin"
    / "hermes-threshold"
    / "dashboard"
    / "plugin_api.py"
)


def load_plugin_api():
    spec = importlib.util.spec_from_file_location("hermes_threshold_dashboard_plugin", PLUGIN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code: int, payload: Any):
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}"
        self.text = str(payload)

    def json(self):
        return self._payload


class FakeAsyncClient:
    requests: list[dict[str, Any]] = []

    def __init__(self, timeout: float):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def request(self, method: str, url: str, **kwargs):
        self.requests.append({"method": method, "url": url, **kwargs})
        if url.endswith("/trial-summary"):
            return FakeResponse(200, {"counts": {"wake_cycles": 3}})
        if url.endswith("/suggestions"):
            return FakeResponse(200, {"suggestions": []})
        if url.endswith("/suggestions/suggestion_1/approve"):
            return FakeResponse(200, {"suggestion": {"status": "approved"}})
        return FakeResponse(200, {"status": "ok"})


def test_dashboard_plugin_proxies_threshold_with_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / "service.env"
    env_file.write_text(
        "HERMES_THRESHOLD_URL=http://127.0.0.1:9999\n"
        "HERMES_THRESHOLD_API_TOKEN=secret-token\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_THRESHOLD_ENV_FILE", str(env_file))

    module = load_plugin_api()
    FakeAsyncClient.requests = []
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    app = FastAPI()
    app.include_router(module.router)

    with TestClient(app) as client:
        summary = client.get("/summary")
        suggestions = client.get("/suggestions?status=drafted&limit=10")
        approved = client.post("/suggestions/suggestion_1/approve")

    assert summary.status_code == 200
    assert summary.json()["counts"]["wake_cycles"] == 3
    assert suggestions.status_code == 200
    assert approved.json()["suggestion"]["status"] == "approved"
    assert FakeAsyncClient.requests[0]["url"] == "http://127.0.0.1:9999/trial-summary"
    assert FakeAsyncClient.requests[0]["headers"] == {"authorization": "Bearer secret-token"}
    assert FakeAsyncClient.requests[1]["params"] == {"limit": 10, "status": "drafted"}
