from __future__ import annotations

from fastapi import Header, HTTPException, status

from hermes_threshold.config import Settings


async def require_api_token(
    settings: Settings,
    authorization: str | None = Header(default=None),
    x_hermes_threshold_token: str | None = Header(default=None),
) -> None:
    if not settings.auth_required:
        return
    if not settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is required but no API token is configured.",
        )

    bearer = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()
    provided = x_hermes_threshold_token or bearer
    if provided != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Hermes Threshold API token.",
        )
