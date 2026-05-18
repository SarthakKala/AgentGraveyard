"""
Async agent with @graveyard.watch_async.

  python demo/demo_async_agent.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk"))

from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

graveyard = GraveyardWrapper(
    api_key="community",
    backend_url=BACKEND_URL,
    verbose=True,
)


@graveyard.watch_async
async def async_agent(task: str) -> str:
    wisdom = get_wisdom_prompt_prefix()
    if wisdom:
        print("Wisdom prefix received for async task.")
    await asyncio.sleep(0.2)
    return "async-ok"


async def main() -> None:
    print("=== Demo: Async watch path ===")
    result = await async_agent(task="Run async agent operation")
    print("Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
