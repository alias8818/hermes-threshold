from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import httpx


def _client(args: argparse.Namespace) -> httpx.Client:
    headers = {}
    token = args.token or os.getenv("HERMES_THRESHOLD_API_TOKEN")
    if token:
        headers["authorization"] = f"Bearer {token}"
    return httpx.Client(base_url=args.base_url, headers=headers, timeout=10.0)


def _print_suggestion(suggestion: dict[str, Any]) -> None:
    print(f"{suggestion['suggestion_id']} [{suggestion['status']}]")
    print(f"  {suggestion['title']}")
    if suggestion.get("description"):
        print(f"  {suggestion['description']}")


def list_suggestions(args: argparse.Namespace) -> int:
    with _client(args) as client:
        response = client.get("/suggestions", params={"status": args.status, "limit": args.limit})
        response.raise_for_status()
    for suggestion in response.json()["suggestions"]:
        _print_suggestion(suggestion)
    return 0


def review_suggestion(args: argparse.Namespace, action: str) -> int:
    with _client(args) as client:
        response = client.post(f"/suggestions/{args.suggestion_id}/{action}")
        response.raise_for_status()
    _print_suggestion(response.json()["suggestion"])
    return 0


def trial_summary(args: argparse.Namespace) -> int:
    with _client(args) as client:
        response = client.get("/trial-summary")
        response.raise_for_status()
    payload = response.json()
    for key, value in payload["counts"].items():
        print(f"{key}: {value}")
    for key in [
        "drafted_suggestions",
        "approved_suggestions",
        "dismissed_suggestions",
        "useful_feedback",
        "annoyance_feedback",
    ]:
        print(f"{key}: {payload[key]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review Hermes Threshold suggestions.")
    parser.add_argument("--base-url", default=os.getenv("HERMES_THRESHOLD_URL", "http://127.0.0.1:8789"))
    parser.add_argument("--token", default=None)
    subcommands = parser.add_subparsers(dest="command", required=True)

    list_parser = subcommands.add_parser("list")
    list_parser.add_argument("--status", default="drafted")
    list_parser.add_argument("--limit", type=int, default=20)
    list_parser.set_defaults(handler=list_suggestions)

    approve_parser = subcommands.add_parser("approve")
    approve_parser.add_argument("suggestion_id")
    approve_parser.set_defaults(handler=lambda args: review_suggestion(args, "approve"))

    dismiss_parser = subcommands.add_parser("dismiss")
    dismiss_parser.add_argument("suggestion_id")
    dismiss_parser.set_defaults(handler=lambda args: review_suggestion(args, "dismiss"))

    summary_parser = subcommands.add_parser("summary")
    summary_parser.set_defaults(handler=trial_summary)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except httpx.HTTPStatusError as exc:
        print(f"HTTP {exc.response.status_code}: {exc.response.text}", file=sys.stderr)
        return 1
    except httpx.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
