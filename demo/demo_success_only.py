import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sdk.agentgraveyard import GraveyardWrapper


graveyard = GraveyardWrapper(
    api_key="community",
    backend_url="http://localhost:8000",
    verbose=True,
)


@graveyard.watch
def add_numbers(task: str, a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    print("=== Demo: Success-only path ===")
    result = add_numbers(task="Add two integers for health-check task", a=20, b=22)
    print("Result:", result)
