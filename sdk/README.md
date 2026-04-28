## Quick Start

pip install agent-graveyard

## Basic Usage (3 lines of integration)

```python
from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(api_key="your-key-here")

@graveyard.watch
def my_agent(task: str) -> str:
    wisdom = get_wisdom_prompt_prefix()
    prompt = wisdom + f"Complete this task: {task}"
    result = f"Stub agent output for: {prompt}"
    return result
```

## Async Support

```python
@graveyard.watch_async
async def my_async_agent(task: str) -> str:
    return "ok"
```

## Manual Wisdom Query

```python
wisdom = await graveyard.query_wisdom("scrape data from e-commerce site")
print(wisdom["wisdom"]["synthesized_recommendation"])
```
