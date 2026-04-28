# Agent Graveyard

Self-healing failure memory system for AI agents.

## The Problem
Production agents repeatedly fail in similar ways, but each run starts cold and re-learns the same lessons. Teams lose time to recurring tool errors, prompt failures, and brittle integrations.

Agent Graveyard solves this by turning every failure into reusable memory. A Coroner Agent diagnoses the failure, stores a structured autopsy + embedding, synthesizes a fix from similar incidents, and attempts autonomous self-healing.

## Architecture
```
SDK Decorator -> Backend API -> Coroner Pipeline -> SQLite + Pinecone
      ^                                              |
      |---------------- Wisdom Injection <-----------|
```

## Demo GIF
_Coming soon_

## How It Works
1. Pre-task wisdom query: retrieve similar failures before execution.
2. Failure autopsy: classify, diagnose, synthesize, and store knowledge.
3. Self-heal loop: retry with synthesized approach and store outcomes.

## SDK Install
```bash
pip install agent-graveyard
```

```python
from agentgraveyard import GraveyardWrapper
graveyard = GraveyardWrapper(api_key="your-key")
@graveyard.watch
def run(task: str):
    return f"running {task}"
```

## Dashboard
_Screenshot placeholder_

## Tech Stack
- Backend: FastAPI, SQLAlchemy, LangGraph
- Memory: Pinecone + local free embeddings (`BAAI/bge-base-en-v1.5`, 768-dim)
- LLM: OpenRouter (single provider for reasoning/coroner synthesis)
- SDK: Python package
- Frontend: Next.js + Tailwind + Recharts

## Self-Hosting
1. Configure `backend/.env.example` values in `.env`.
2. Run backend and dashboard via Docker Compose.
3. Seed community failures with `python seed_data/seed.py`.

## Contributing
Issues and PRs are welcome. Keep changes scoped by stage (`1.x`, `2.x`, `3.x`, `4.x`) to align with project milestones.