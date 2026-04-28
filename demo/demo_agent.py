from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix
import requests
from bs4 import BeautifulSoup

graveyard = GraveyardWrapper(api_key="demo-key", backend_url="http://localhost:8000", verbose=True)


@graveyard.watch
def scrape_prices(url: str) -> list[str]:
    wisdom = get_wisdom_prompt_prefix()
    if wisdom:
        print(f"Agent received wisdom: {wisdom[:120]}...")
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    prices = soup.find_all(class_="price")
    if not prices:
        raise ValueError("No prices found - page may require JavaScript rendering")
    return [p.get_text(strip=True) for p in prices]


if __name__ == "__main__":
    print("=== Run 1: Expecting failure ===")
    try:
        scrape_prices("https://books.toscrape.com")
    except Exception as exc:
        print(f"Failed as expected: {exc}")

    import time

    time.sleep(3)
    print("\n=== Run 2: With wisdom from graveyard ===")
    try:
        result = scrape_prices("https://books.toscrape.com")
        print(f"Success: {result}")
    except Exception as exc:
        print(f"Run 2 still failed: {exc}")
