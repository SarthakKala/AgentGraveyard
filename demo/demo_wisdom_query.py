import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sdk.agentgraveyard import GraveyardWrapper


async def main() -> None:
    graveyard = GraveyardWrapper(
        api_key="community",
        backend_url="http://localhost:8000",
        verbose=False,
    )
    print("=== Demo: Direct wisdom query ===")
    wisdom = await graveyard.query_wisdom("Scrape JS-heavy ecommerce site prices")
    print(wisdom)


if __name__ == "__main__":
    asyncio.run(main())
