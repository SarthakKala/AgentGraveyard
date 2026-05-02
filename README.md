# 🪦 Agent Graveyard

> Self-healing failure memory for AI agents.  
> When your agent fails, it learns. Forever.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-orange.svg)](https://openrouter.ai)
[![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-purple.svg)](https://pinecone.io)

---

Most AI agents have a fatal flaw. When they fail, the failure disappears.

You debug it. You fix it. You move on. Two weeks later, a different agent makes the exact same mistake.

**Agent Graveyard fixes this.**

When your agent fails, a **Coroner Agent** automatically diagnoses what went wrong, synthesizes a solution from similar past failures, and stores the lesson in a vector database. Every future agent queries this collective memory before it starts — inheriting the knowledge of every failure that came before it.

The integration is **a few lines of code** added to your existing agent:

```python
from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(
    api_key="community",
    backend_url="http://localhost:8000",
    verbose=True,
)

@graveyard.watch                    # ← wrap your function
def my_agent(task: str) -> str:     # your existing function
    wisdom = get_wisdom_prompt_prefix()   # optional: injected wisdom
    # rest of your agent code here
    ...
```

---

## What You See In Your Terminal

With **`verbose=True`**, the SDK uses **Rich** for colored output — wisdom scans, failures, coroner/self-heal messages, and success lines. Exact wording depends on your backend configuration and whether similar failures exist in the graveyard.

Example flavor:

```
[AgentGraveyard] Pre-task wisdom scan...
[AgentGraveyard] No warnings found.
[AgentGraveyard] Agent FAILED: ValueError — ...
[AgentGraveyard] Coroner Agent diagnosing...
```

---

## Quick Start

→ **See [QUICKSTART.md](QUICKSTART.md) for full step-by-step setup.**

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard
cp backend/.env.example backend/.env
# fill in your API keys (Pinecone + OpenRouter + Neon — all free)
bash run.sh
# new terminal → python demo/demo_agent.py
```

---

## How It Works

```
Your agent starts a task
         ↓
Queries graveyard for similar past failures (embeddings + Pinecone)
         ↓
Wisdom can be injected into agent context before it runs
         ↓
Agent runs with inherited knowledge
         ↓
       SUCCESS?
      ↙        ↘
    YES          NO
     ↓            ↓
 Log success   Coroner diagnoses WHY it failed
               → Classifies: TOOL / PROMPT / DATA / ENV / REASONING
               → Retrieves similar past failures
               → Synthesizes guidance via LLM (OpenRouter)
               → Self-heal path when enabled
               → Stores structured outcome (Postgres + vectors)
         ↓
 Graveyard improves with every recorded failure
```

### Why This Is Not Just "A Database With Embeddings"

The naive version: store failure → query → return a canned answer.

Agent Graveyard **structures** failures, **retrieves** semantically similar incidents, and uses the **LLM** to synthesize guidance grounded in past lessons — combining multiple signals instead of simple autocomplete.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  Your Agent Code                            │
│  @graveyard.watch                           │
└──────────────┬──────────────────────────────┘
               │ HTTP / WebSocket
┌──────────────▼──────────────────────────────┐
│  Agent Graveyard Backend (FastAPI)          │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ Coroner     │  │ Self-Healer          │  │
│  │ pipeline    │  │                      │  │
│  └──────┬──────┘  └──────────────────────┘  │
│         │                                   │
│  ┌──────▼──────────────────────────────┐    │
│  │ Local Embeddings                    │    │
│  │ (BAAI/bge-base-en-v1.5, local GPU/CPU)   │
│  └──────┬──────────────────────────────┘    │
└─────────┼───────────────────────────────────┘
          │
    ┌─────┴──────┐
    │            │
┌───▼───┐  ┌────▼────┐
│Pinecone│  │Postgres │
│Vectors │  │(Neon)   │
└────────┘  └─────────┘
```

**Key design decision: embeddings are local.**  
We use `sentence-transformers` with `BAAI/bge-base-en-v1.5` — runs on your machine, no paid embedding API.

**LLM via OpenRouter.**  
Default in `.env.example`: `mistralai/mistral-7b-instruct:free` — free tier friendly.

---

## CLI

```bash
graveyard --backend-url http://localhost:8000 health
graveyard --backend-url http://localhost:8000 doctor
graveyard overview --backend-url http://localhost:8000 --api-key community
graveyard recent --backend-url http://localhost:8000 --api-key community
graveyard wisdom --backend-url http://localhost:8000 --api-key community --task "your task description"
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| SDK | Python, Rich, httpx, websockets |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL (Neon) or SQLite |
| Vector DB | Pinecone (free tier) |
| Embeddings | `sentence-transformers` — **local** |
| LLM | OpenRouter — free models available |
| Containerization | Docker + Docker Compose |

---

## SQLite vs Postgres (concurrency)

SQLite allows **one writer at a time**. Multiple concurrent agents or several FastAPI workers hitting the same SQLite file can produce **database is locked** errors or stalled writes. **Neon (Postgres)** is the better default for demos that involve concurrent SDK traffic or `uvicorn --workers` greater than one.

Practical guidance:

- **Toy single-agent demos on one machine:** SQLite is fine if you run **one backend process** (`workers=1`).
- **Anything with concurrent clients or production-ish load:** use **Postgres** (see `DATABASE_URL` in `backend/.env.example`) and keep the backend to a single worker only if you deliberately accept SQLite limits.

---

## Roadmap / deferred work

The following are **not** in the current reliability pass but are reasonable follow-ups:

- **Deduplication:** merge or bump counts when the same failure signature appears repeatedly (e.g. hash of normalized error + similar task embedding).
- **Pinecone metadata size:** truncate long `lesson` / `suggested_approach` fields before upsert so metadata stays within provider limits; keep full text in Postgres.

---

## Pre-Seeded Community Failures

On first run, `seed_data/seed.py` loads **`seed_data/common_failures.json`** (large curated set) into Postgres and Pinecone so wisdom retrieval has data to match. You get immediate signal before your own agents fail.

---

## Contributing Failures

Add real failures to `seed_data/common_failures.json` using the shape described in that file (task, error, lesson, category, etc.). Optional: `source_citations` for URLs.

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built for agents that should learn from every mistake.*
