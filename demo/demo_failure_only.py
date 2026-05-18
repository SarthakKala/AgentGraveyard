"""
Single failure → coroner (LangGraph) + self-heal bookkeeping.
Uses share_with_community=True to test community persistence.

  python demo/demo_failure_only.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk"))

from agentgraveyard import GraveyardWrapper

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

graveyard = GraveyardWrapper(
    api_key="community",
    backend_url=BACKEND_URL,
    verbose=True,
    share_with_community=True,
)


@graveyard.watch
def always_fail(task: str) -> None:
    raise RuntimeError("Intentional demo failure to test coroner + self-heal pipeline logging")


if __name__ == "__main__":
    print("=== Demo: Failure-only path ===")
    try:
        always_fail(task="Trigger a deterministic failure")
    except Exception as exc:
        print(f"Caught expected exception: {exc}")
