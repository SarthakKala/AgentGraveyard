"""
🪦 Agent Graveyard — Live Demo
================================
Shows the self-healing failure memory flow (SDK + backend).

Run from repo root:
    python demo/demo_agent.py

Requirements:
    - Backend running on http://localhost:8000 (e.g. bash run.sh)
    - backend/.env configured with your API keys
    - pip install -e ./sdk
"""

import os
import sys
import time
from pathlib import Path

import requests

# Allow running from repo root without pip install (development)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk"))

from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

# ── Setup ─────────────────────────────────────────────────────────

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

print()
print("=" * 60)
print("🪦  AGENT GRAVEYARD — LIVE DEMO")
print("=" * 60)
print()
print("This demo exercises the SDK against the backend:")
print("  Run 1 → Agent fails → events logged to backend")
print("  Run 2 → Wisdom may appear if the graveyard has similar failures")
print()

# Check backend is running
try:
    resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if resp.status_code == 200:
        print("✅  Backend is running on", BACKEND_URL)
    else:
        raise RuntimeError(f"Status {resp.status_code}")
except Exception as e:
    print(f"❌  Cannot reach backend at {BACKEND_URL}")
    print(f"   Error: {e}")
    print()
    print("   Start the backend first:")
    print("   bash run.sh")
    print("   # or: cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
    print()
    sys.exit(1)

print()

graveyard = GraveyardWrapper(
    api_key="community",
    backend_url=BACKEND_URL,
    verbose=True,
)


# ── Agent Definition ──────────────────────────────────────────────


@graveyard.watch
def scraping_agent(task: str) -> list:
    """
    A web scraping agent.
    Uses a selector that does not exist on the demo page to trigger a clear failure.
    """
    wisdom = get_wisdom_prompt_prefix()
    if wisdom:
        print()
        print("  ┌─ Wisdom Received From Graveyard ────────────────┐")
        for line in wisdom.strip().split("\n"):
            if line.strip():
                print(f"  │  {line}")
        print("  └─────────────────────────────────────────────────┘")
        print()

    response = requests.get("https://books.toscrape.com", timeout=10)
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, "html.parser")

    # Wrong selector — deterministic empty result (simulates “wrong tool / DOM” lessons)
    prices = soup.find_all(class_="js-rendered-dynamic-price")

    if not prices:
        raise ValueError(
            "No prices found. Selector for '.js-rendered-dynamic-price' "
            "returned 0 elements (demo failure for Agent Graveyard)."
        )

    return [p.text.strip() for p in prices]


# ── RUN 1 ─────────────────────────────────────────────────────────

print("-" * 60)
print("RUN 1 — First attempt (expect failure for demo)")
print("-" * 60)
print()

try:
    scraping_agent(task="Scrape book prices from an e-commerce website")
except (ValueError, Exception):
    pass

print()
print("⏳  Pausing briefly so logs / backend work can finish...")
time.sleep(3)

# ── RUN 2 ─────────────────────────────────────────────────────────

print()
print("-" * 60)
print("RUN 2 — Second attempt (wisdom may appear if DB/Pinecone have matches)")
print("-" * 60)
print()

try:
    scraping_agent(task="Scrape book prices from an e-commerce website")
except (ValueError, Exception):
    pass

# ── SUMMARY ───────────────────────────────────────────────────────

print()
print("=" * 60)
print("🪦  DEMO COMPLETE")
print("=" * 60)
print()
print("What happened:")
print("  • The SDK ran a pre-task wisdom query each time (see [AgentGraveyard] lines).")
print("  • The agent raised ValueError — failure events were sent to the backend.")
print("  • With seeded data + Pinecone, Run 2 may show injected wisdom above.")
print()
print("Explore data with the CLI (from repo root, venv on):")
print("  graveyard doctor --backend-url http://localhost:8000")
print("  graveyard recent --backend-url http://localhost:8000 --api-key community")
print(
    "  graveyard wisdom --backend-url http://localhost:8000 --api-key community "
    '--task "scrape a JavaScript-heavy website"'
)
print()
print("=" * 60)
print()
