"""
Environment checker for Agent Graveyard.
Run: python scripts/check_env.py
Exits with code 0 if all checks pass, 1 if anything is missing.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _load_backend_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def _is_placeholder(val: str) -> bool:
    v = val.strip()
    if not v:
        return True
    low = v.lower()
    if low.startswith("your_") or low.endswith("_here"):
        return True
    if "your_pinecone" in low or "your_openrouter" in low:
        return True
    # Neon template from docs / example
    if "postgresql" in low and "user:password@host" in low:
        return True
    if "CHANGE_ME" in v or "changeme" in low:
        return True
    return False


_env_file = Path(__file__).resolve().parent.parent / "backend" / ".env"
if not _env_file.exists():
    print()
    print("Agent Graveyard - Environment Check")
    print("=" * 50)
    print()
    print("  [X]  backend/.env not found")
    print("      Run: cp backend/.env.example backend/.env")
    print("      Then add Pinecone, OpenRouter, and DATABASE_URL.")
    print()
    sys.exit(1)

_load_backend_dotenv()

# Prefer Neon URL if DATABASE_URL empty
if not os.environ.get("DATABASE_URL", "").strip() and os.environ.get("NEON_DATABASE_URL", "").strip():
    os.environ["DATABASE_URL"] = os.environ["NEON_DATABASE_URL"].strip()

# ── Check definitions ─────────────────────────────────────────────
checks = [
    {
        "key": "PINECONE_API_KEY",
        "label": "Pinecone API Key",
        "help": "Get it at: https://pinecone.io → Dashboard → API Keys",
    },
    {
        "key": "PINECONE_INDEX_NAME",
        "label": "Pinecone Index Name",
        "help": "Set to 'agent-graveyard' in backend/.env",
        "default": "agent-graveyard",
    },
    {
        "key": "OPENROUTER_API_KEY",
        "label": "OpenRouter API Key",
        "help": "Get it at: https://openrouter.ai → Dashboard → Keys",
    },
    {
        "key": "OPENROUTER_MODEL",
        "label": "OpenRouter Model",
        "help": "Set to 'mistralai/mistral-7b-instruct:free' for free usage",
        "default": "mistralai/mistral-7b-instruct:free",
    },
    {
        "key": "DATABASE_URL",
        "label": "Database URL",
        "help": (
            "Neon (free): https://neon.tech → New Project → Connection String\n"
            "      Or use SQLite locally: DATABASE_URL=sqlite:///./graveyard.db"
        ),
    },
]

# ── Run checks ────────────────────────────────────────────────────
print()
print("Agent Graveyard - Environment Check")
print("=" * 50)

all_passed = True

for check in checks:
    key = check["key"]
    val = os.environ.get(key, "").strip()
    default = check.get("default", "")

    if not val and default:
        val = default
        os.environ.setdefault(key, val)

    if val and not _is_placeholder(val):
        print(f"  [OK]  {check['label']}")
    else:
        print(f"  [X]  {check['label']} - MISSING or placeholder")
        print(f"      {check['help']}")
        all_passed = False

print()

# ── Check Python version ──────────────────────────────────────────
py = sys.version_info
if py.major == 3 and py.minor >= 10:
    print(f"  [OK]  Python {py.major}.{py.minor}.{py.micro}")
else:
    print(f"  [X]  Python {py.major}.{py.minor}.{py.micro} - Need Python 3.10+")
    all_passed = False

# ── Check SDK installed ───────────────────────────────────────────
try:
    import agentgraveyard  # noqa: F401

    print("  [OK]  SDK installed (agentgraveyard)")
except ImportError:
    print("  [X]  SDK not installed - run: pip install -e ./sdk")
    all_passed = False

# ── Check Rich installed ──────────────────────────────────────────
try:
    import rich  # noqa: F401

    print("  [OK]  Rich (terminal formatting)")
except ImportError:
    print("  [X]  Rich not installed - run: pip install rich")
    all_passed = False

print()

if all_passed:
    print("[OK]  All checks passed. You are ready to run:")
    print("   python demo/demo_agent.py")
    print()
    sys.exit(0)
else:
    print("[X]  Fix the issues above, then run this script again.")
    print()
    sys.exit(1)
