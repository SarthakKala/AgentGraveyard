"""
Success-only path: TASK_START → agent returns → TASK_SUCCESS.

  python demo/demo_success_only.py
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
)


@graveyard.watch
def add_numbers(task: str, a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print("=== Demo: Success-only path ===")
    result = add_numbers(task="Add two integers for health-check task", a=20, b=22)
    print("Result:", result)
