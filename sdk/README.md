# agent-graveyard (Python SDK)

Self-healing failure memory for AI agents: wrap functions with `@graveyard.watch`, query wisdom before tasks, and use the **`graveyard` CLI** for visibility.

## Install

From the repository root (editable dev install):

```bash
pip install -e ./sdk
```

This exposes the `graveyard` console script.

## Quick integration

```python
from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(api_key="your-key-here", backend_url="http://localhost:8000", verbose=True)

@graveyard.watch
def my_agent(task: str) -> str:
    wisdom = get_wisdom_prompt_prefix()
    prompt = (wisdom or "") + f"Complete this task: {task}"
    return f"Result for: {prompt}"
```

## Async

```python
@graveyard.watch_async
async def my_async_agent(task: str) -> str:
    return "ok"
```

## Manual wisdom query

```python
wisdom = await graveyard.query_wisdom("scrape data from e-commerce site")
print(wisdom["wisdom"]["synthesized_recommendation"])
```

## CLI

`--backend-url` and `--json` may appear before or after the subcommand:

```bash
graveyard --backend-url http://localhost:8000 doctor
graveyard doctor --backend-url http://localhost:8000
graveyard recent --api-key community --limit 10 --backend-url http://localhost:8000
graveyard --json health
```

See `graveyard --help` and the main repository `README.md` for the full verification checklist.
