from __future__ import annotations

import httpx

from hermes_threshold import cli


def test_cli_list_suggestions(monkeypatch, capsys):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/suggestions"
        return httpx.Response(
            200,
            json={
                "suggestions": [
                    {
                        "suggestion_id": "suggestion_test",
                        "cycle_id": "cycle_test",
                        "created_at": "2026-05-07T14:00:00Z",
                        "title": "Draft action tiers",
                        "description": "Review action tiers.",
                        "status": "drafted",
                        "payload": {},
                    }
                ]
            },
        )

    transport = httpx.MockTransport(handler)

    class MockClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = transport
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(cli.httpx, "Client", MockClient)

    result = cli.main(["--base-url", "http://testserver", "list"])

    assert result == 0
    assert "suggestion_test [drafted]" in capsys.readouterr().out
