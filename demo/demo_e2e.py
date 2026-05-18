"""
Agent Graveyard — end-to-end verification (SDK + backend + recent fixes).

Run from repo root with the backend already up (run.sh / run.ps1):

    .venv\\Scripts\\Activate.ps1          # Windows
    python demo/demo_e2e.py

Optional:
    set BACKEND_URL=http://127.0.0.1:8000

What this script checks:
  1. Backend /health
  2. API key is SHA-256 hashed before HTTP calls (not sent raw)
  3. Sync @graveyard.watch works inside a running asyncio loop
  4. share_with_community persists (DB + coroner / LangGraph path)
  5. watch_async success path
  6. Wisdom API returns a briefing for a scrape-style task

Individual demos (same folder):
  demo_agent.py          — full scrape failure + wisdom on run 2
  demo_wisdom_query.py   — readable wisdom output
  demo_failure_only.py   — coroner on a single failure
  demo_success_only.py   — TASK_SUCCESS only
  demo_async_agent.py    — watch_async
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import uuid
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk"))

from agentgraveyard import GraveyardWrapper
from agentgraveyard.identity import api_key_hash

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000").rstrip("/")
RAW_KEY = "community"
KEY_HASH = api_key_hash(RAW_KEY)


class CheckResult:
    def __init__(self, name: str, ok: bool, detail: str = ""):
        self.name = name
        self.ok = ok
        self.detail = detail


results: list[CheckResult] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append(CheckResult(name, ok, detail))
    mark = "OK" if ok else "FAIL"
    line = f"  [{mark}] {name}"
    if detail:
        line += f" - {detail}"
    print(line)


def _field(row: object, key: str):
    if isinstance(row, dict):
        return row.get(key)
    return getattr(row, key, None)


def _is_truthy(val: object) -> bool:
    if val is True or val == 1:
        return True
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes")
    return bool(val)


def check_health(client: httpx.Client) -> bool:
    try:
        r = client.get(f"{BACKEND_URL}/health", timeout=15.0)
        r.raise_for_status()
        body = r.json()
        ok = body.get("status") in ("ok", "degraded")
        record("Backend /health", ok, f"status={body.get('status')}, version={body.get('version')}")
        return ok
    except Exception as exc:
        record("Backend /health", False, str(exc))
        return False


def check_api_key_hashing() -> GraveyardWrapper | None:
    try:
        g = GraveyardWrapper(api_key=RAW_KEY, backend_url=BACKEND_URL, verbose=False)
        ok = g.client.api_key_hash == KEY_HASH and g.client.api_key_hash != RAW_KEY
        record(
            "API key hashing (SDK client)",
            ok,
            f"hash prefix {g.client.api_key_hash[:12]}…" if ok else "client still sends raw key",
        )
        return g if ok else None
    except Exception as exc:
        record("API key hashing (SDK client)", False, str(exc))
        return None


def check_wisdom_api(client: httpx.Client) -> bool:
    try:
        r = client.get(
            f"{BACKEND_URL}/api/sdk/wisdom",
            params={"task": "Scrape JS-heavy ecommerce site prices", "api_key_hash": KEY_HASH},
            timeout=60.0,
        )
        r.raise_for_status()
        w = r.json().get("wisdom") or {}
        ok = isinstance(w, dict)
        detail = (
            f"has_warnings={w.get('has_warnings')}, "
            f"confidence={w.get('confidence_score')}, "
            f"matches={len(w.get('similar_failures') or [])}"
        )
        record("Wisdom API (hashed key)", ok, detail)
        return ok
    except Exception as exc:
        record("Wisdom API (hashed key)", False, str(exc))
        return False


def check_nested_event_loop(graveyard: GraveyardWrapper) -> bool:
    @graveyard.watch
    def add_one(task: str, n: int) -> int:
        return n + 1

    async def run_inside_loop() -> int:
        return add_one(task="E2E nested asyncio loop check", n=41)

    try:
        value = asyncio.run(run_inside_loop())
        ok = value == 42
        record("Sync watch() inside asyncio.run()", ok, f"returned {value}")
        return ok
    except RuntimeError as exc:
        if "asyncio.run()" in str(exc):
            record("Sync watch() inside asyncio.run()", False, "event loop conflict (run_coro_sync missing?)")
        else:
            record("Sync watch() inside asyncio.run()", False, str(exc))
        return False
    except Exception as exc:
        record("Sync watch() inside asyncio.run()", False, str(exc))
        return False


def check_share_with_community(graveyard: GraveyardWrapper, client: httpx.Client) -> bool:
    shared = GraveyardWrapper(
        api_key=RAW_KEY,
        backend_url=BACKEND_URL,
        verbose=False,
        share_with_community=True,
    )
    marker = f"E2E share_with_community {uuid.uuid4().hex[:8]}"

    @shared.watch
    def fail_for_community(task: str) -> None:
        raise RuntimeError(f"E2E community share test {uuid.uuid4().hex[:8]}")

    try:
        try:
            fail_for_community(task=marker)
        except RuntimeError:
            pass

        ok_row = None
        last_count = 0
        for attempt in range(20):
            time.sleep(3)
            r = client.get(f"{BACKEND_URL}/api/failures/community", timeout=60.0)
            r.raise_for_status()
            rows = r.json()
            if not isinstance(rows, list):
                rows = []
            last_count = len(rows)
            ok_row = next(
                (
                    row
                    for row in rows
                    if marker in str(_field(row, "task_description") or "")
                    and _is_truthy(_field(row, "is_community_shared"))
                ),
                None,
            )
            if ok_row is not None:
                break

        ok = ok_row is not None
        rid = str(_field(ok_row, "id") or "")[:8] if ok_row else ""
        if ok:
            detail = f"found shared row id={rid} after poll (community total={last_count})"
        else:
            detail = (
                f"no shared row for task marker after ~60s "
                f"(community endpoint returned {last_count} shared rows)"
            )
        record("share_with_community -> DB", ok, detail)
        return ok
    except Exception as exc:
        record("share_with_community -> DB", False, str(exc) or repr(exc))
        return False


async def check_watch_async(graveyard: GraveyardWrapper) -> bool:
    @graveyard.watch_async
    async def async_ok(task: str) -> str:
        await asyncio.sleep(0.05)
        return "async-ok"

    try:
        out = await async_ok(task="E2E async watch check")
        ok = out == "async-ok"
        record("watch_async success path", ok, repr(out))
        return ok
    except Exception as exc:
        record("watch_async success path", False, str(exc))
        return False


def check_overview_hashed(client: httpx.Client) -> bool:
    try:
        r = client.get(
            f"{BACKEND_URL}/api/analytics/overview",
            params={"api_key_hash": KEY_HASH},
            timeout=20.0,
        )
        r.raise_for_status()
        body = r.json()
        ok = "total_failures" in body
        record(
            "Analytics overview (hashed key)",
            ok,
            f"total_failures={body.get('total_failures')}, successes={body.get('total_successes')}",
        )
        return ok
    except Exception as exc:
        record("Analytics overview (hashed key)", False, str(exc))
        return False


def main() -> int:
    print()
    print("=" * 60)
    print("Agent Graveyard — E2E verification")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"Raw key: {RAW_KEY!r}  →  hash prefix: {KEY_HASH[:16]}…")
    print()

    with httpx.Client() as client:
        if not check_health(client):
            print()
            print("Start the backend first: .\\run.ps1  or  bash run.sh")
            return 1

        graveyard = check_api_key_hashing()
        if graveyard is None:
            return 1

        check_wisdom_api(client)
        check_nested_event_loop(graveyard)
        check_share_with_community(graveyard, client)
        asyncio.run(check_watch_async(graveyard))
        check_overview_hashed(client)

    passed = sum(1 for r in results if r.ok)
    total = len(results)
    print()
    print("=" * 60)
    print(f"Result: {passed}/{total} checks passed")
    if passed == total:
        print("All automated checks passed.")
        print()
        print("Optional manual demos:")
        print("  python demo/demo_agent.py")
        print("  python demo/demo_wisdom_query.py")
        print("  graveyard doctor --backend-url", BACKEND_URL)
    else:
        print("Some checks failed — see lines marked FAIL above.")
    print("=" * 60)
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
