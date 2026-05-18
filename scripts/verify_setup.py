#!/usr/bin/env python3
"""
Smoke-check that the backend is up and optional analytics respond.
Run from repository root with the backend already started.

  python scripts/verify_setup.py
  python scripts/verify_setup.py --backend-url http://127.0.0.1:8000 --api-key community
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys


def _api_key_hash(raw_key: str) -> str:
    return hashlib.sha256(raw_key.strip().encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Agent Graveyard backend connectivity.")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default="community", help="raw API key for overview probe (hashed before request)")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()

    try:
        import httpx
    except ImportError:
        print("Install httpx: pip install httpx", file=sys.stderr)
        return 1

    base = args.backend_url.rstrip("/")
    out: dict = {"backend_url": base, "steps": []}

    try:
        r = httpx.get(f"{base}/health", timeout=15.0)
        r.raise_for_status()
        health = r.json()
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}))
        else:
            print(f"[fail] GET /health — {exc}", file=sys.stderr)
            print("Start the API: cd backend && python -m uvicorn main:app --reload --port 8000", file=sys.stderr)
        return 1

    out["steps"].append({"name": "health", "ok": True, "status": health.get("status"), "version": health.get("version")})

    key_hash = _api_key_hash(args.api_key)
    try:
        r2 = httpx.get(
            f"{base}/api/analytics/overview",
            params={"api_key_hash": key_hash},
            timeout=20.0,
        )
        r2.raise_for_status()
        overview = r2.json()
        out["steps"].append({"name": "overview", "ok": True, "total_failures": overview.get("total_failures")})
    except Exception as exc:
        out["steps"].append({"name": "overview", "ok": False, "detail": str(exc)})

    ok = health.get("status") == "ok" and out["steps"][-1].get("ok", False)

    if args.json:
        out["ok"] = ok
        print(json.dumps(out, indent=2))
        return 0 if ok else 1

    print(f"Health: {health.get('status')} (API v{health.get('version')})")
    checks = health.get("checks") or {}
    for name, row in checks.items():
        mark = "OK" if row.get("ok") else "NO"
        extra = f" — {row.get('detail')}" if row.get("detail") else ""
        print(f"  [{mark}] {name}{extra}")

    last = out["steps"][-1]
    if last.get("name") == "overview" and last.get("ok"):
        print(f"Overview probe OK (api_key={args.api_key!r}, total_failures={last.get('total_failures')}).")
    elif last.get("name") == "overview":
        print(f"Overview probe failed: {last.get('detail')}", file=sys.stderr)

    if health.get("status") != "ok":
        print("\nRun: graveyard doctor --backend-url " + base, file=sys.stderr)
        return 1
    if not last.get("ok"):
        return 1
    print("\nAll verify steps passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
