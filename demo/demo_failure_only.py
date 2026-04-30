import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sdk.agentgraveyard import GraveyardWrapper


graveyard = GraveyardWrapper(
    api_key="community",
    backend_url="http://localhost:8000",
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
