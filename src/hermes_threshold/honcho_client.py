from __future__ import annotations

from typing import Any

from hermes_threshold.config import Settings
from hermes_threshold.models import WakeRequest


class HonchoReadOnlyContext:
    def __init__(self, settings: Settings):
        self.settings = settings

    def retrieve(self, request: WakeRequest) -> dict[str, Any]:
        if not self.settings.honcho_api_key:
            return {
                "source": "fallback",
                "enabled": False,
                "reason": "HONCHO_API_KEY is not configured.",
                "peer_card": [],
                "peer_context_summary": "Honcho retrieval disabled; using event payload only.",
                "open_loops": [],
                "event": request.event,
            }

        try:
            from honcho import Honcho
        except Exception as exc:  # pragma: no cover - environment dependent
            return {
                "source": "fallback",
                "enabled": False,
                "reason": f"Honcho SDK import failed: {exc}",
                "peer_card": [],
                "peer_context_summary": "Honcho retrieval unavailable; using event payload only.",
                "open_loops": [],
                "event": request.event,
            }

        try:
            client = Honcho(
                workspace_id=self.settings.workspace_id,
                api_key=self.settings.honcho_api_key,
                environment=self.settings.honcho_environment,
            )
            user = client.peer(self.settings.user_peer_id)
            context = user.context(search_query=self.settings.honcho_context_query)
            peer_card = getattr(context, "peer_card", []) or []
            representation = getattr(context, "representation", None) or getattr(
                context,
                "peer_representation",
                "",
            )
            return {
                "source": "honcho",
                "enabled": True,
                "reason": "Read-only Honcho context retrieved.",
                "peer_card": list(peer_card),
                "peer_context_summary": str(representation or ""),
                "open_loops": [],
                "event": request.event,
            }
        except Exception as exc:
            return {
                "source": "fallback",
                "enabled": False,
                "reason": f"Honcho retrieval failed: {exc}",
                "peer_card": [],
                "peer_context_summary": "Honcho retrieval failed; using event payload only.",
                "open_loops": [],
                "event": request.event,
            }
