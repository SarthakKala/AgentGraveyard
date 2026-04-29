# Agent Graveyard (SDK-First Mode)

Self-healing failure memory system for AI agents, designed to run primarily through Python SDK + backend API.

## Why SDK-first
Production agents often repeat the same failures. Agent Graveyard captures those incidents as reusable memory and injects warnings before future runs.

Core value is in:
- automatic event capture from your code
- centralized failure memory store
- pre-task wisdom retrieval
- terminal-first visibility via colored logs

## Core Architecture
```text
Your Python Agent
  -> GraveyardWrapper decorator
    -> Backend API (FastAPI)
      -> Coroner + synthesis pipeline (OpenRouter)
      -> SQL memory + Pinecone vectors (+ local BGE embeddings)
```

## Quick Start

### 1) Start backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2) Seed shared memory
From project root:
```bash
python seed_data/seed.py --force
```

### 3) Use SDK in your code
```python
from sdk.agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(
    api_key="your-api-key-or-hash",
    backend_url="http://localhost:8000",
    verbose=True,
)

@graveyard.watch
def run_agent(task: str):
    wisdom = get_wisdom_prompt_prefix()
    if wisdom:
        print("Wisdom injected:\n", wisdom)
    # your agent logic...
    return "ok"
```

## Terminal CLI (optional but recommended)
After installing SDK package locally, you can use:
```bash
graveyard health --backend-url http://localhost:8000
graveyard overview --backend-url http://localhost:8000 --api-key community
graveyard recent --backend-url http://localhost:8000 --api-key community --limit 10
graveyard wisdom --backend-url http://localhost:8000 --api-key community --task "scrape dynamic prices"
```

## Tech Stack
- Backend: FastAPI, SQLAlchemy, LangGraph
- LLM reasoning: OpenRouter
- Embeddings: local `BAAI/bge-base-en-v1.5` (768 dim)
- Vector memory: Pinecone
- SDK: Python + Rich terminal logs

## Notes
- API key handling in this repo currently uses `api_key_hash` semantics in endpoints.
- For true multi-tenant production use, enforce hashing + auth middleware server-side.