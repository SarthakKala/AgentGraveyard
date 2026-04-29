import argparse
import json
from typing import Any

import httpx


def _api(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def cmd_health(args: argparse.Namespace) -> int:
    try:
        r = httpx.get(_api(args.backend_url, "/health"), timeout=15.0)
        r.raise_for_status()
    except Exception as exc:
        print(f"[graveyard] health check failed: {exc}")
        return 1
    print(json.dumps(r.json(), indent=2))
    return 0


def cmd_overview(args: argparse.Namespace) -> int:
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/analytics/overview"),
            params={"api_key_hash": args.api_key},
            timeout=20.0,
        )
        r.raise_for_status()
    except Exception as exc:
        print(f"[graveyard] overview failed: {exc}")
        return 1
    print(json.dumps(r.json(), indent=2))
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/failures"),
            params={"api_key_hash": args.api_key, "page": 1, "page_size": args.limit},
            timeout=20.0,
        )
        r.raise_for_status()
    except Exception as exc:
        print(f"[graveyard] recent failures failed: {exc}")
        return 1

    payload = r.json()
    items: list[dict[str, Any]] = payload.get("items", [])
    print(f"[graveyard] total={payload.get('total', 0)} showing={len(items)}")
    for i, item in enumerate(items, start=1):
        print(f"{i:02d}. {item.get('id')} | {item.get('failure_category')} | {item.get('agent_name')}")
        print(f"    task: {item.get('task_description')}")
    return 0


def cmd_wisdom(args: argparse.Namespace) -> int:
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/sdk/wisdom"),
            params={"task": args.task, "api_key_hash": args.api_key},
            timeout=25.0,
        )
        r.raise_for_status()
    except Exception as exc:
        print(f"[graveyard] wisdom query failed: {exc}")
        return 1

    print(json.dumps(r.json(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="graveyard", description="Terminal CLI for Agent Graveyard SDK mode")
    p.add_argument("--backend-url", default="http://localhost:8000", help="Backend API base URL")

    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("health", help="Check backend health")
    h.set_defaults(func=cmd_health)

    o = sub.add_parser("overview", help="Show analytics overview for API key")
    o.add_argument("--api-key", required=True, help="API key hash (or SDK key if your backend uses raw key)")
    o.set_defaults(func=cmd_overview)

    r = sub.add_parser("recent", help="List recent failures")
    r.add_argument("--api-key", required=True, help="API key hash (or SDK key if your backend uses raw key)")
    r.add_argument("--limit", type=int, default=10, help="Max rows to display (backend limit <= 100)")
    r.set_defaults(func=cmd_recent)

    w = sub.add_parser("wisdom", help="Query wisdom for task text")
    w.add_argument("--api-key", required=True, help="API key hash (or SDK key if your backend uses raw key)")
    w.add_argument("--task", required=True, help="Task description to evaluate")
    w.set_defaults(func=cmd_wisdom)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
