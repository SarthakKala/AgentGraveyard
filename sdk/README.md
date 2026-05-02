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

### Task text for wisdom / events

The wrapper needs a **human-readable task string** for wisdom queries and backend events. Resolution order:

1. If you passed `GraveyardWrapper(task_param="my_task")`, the keyword argument **`my_task`** is used when present.
2. Otherwise **`task_description=`** or **`task=`** in the wrapped call.
3. Otherwise the **first positional argument** — with a **warning** if there are multiple positional args and no explicit task keyword.

For non-trivial signatures, prefer **`task_description=`** or **`task=`** (or set **`task_param`**) so wisdom never picks the wrong argument.

### Wisdom is not auto-injected

`get_wisdom_prompt_prefix()` returns text you should **merge into your prompt** (prepend or concatenate). The SDK does not silently change model inputs unless your code uses that string.

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
