# AgentGraveyard

AgentGraveyard is a self-healing failure memory system for AI agents. Production agents often repeat the same failures because they have no durable memory of what went wrong. AgentGraveyard captures failures, turns them into structured incidents, stores embeddings in Pinecone, and can inject relevant warnings into the prompt before the next run. **This repo is optimized for SDK-first / terminal workflows** (Python decorator + CLI); there is no bundled web dashboard.

---

## Prerequisites

- **Python 3.11+** (64-bit recommended; avoids older wheels building NumPy from source).
- **Accounts / keys:** Neon (or another Postgres), Pinecone, OpenRouter — see environment table below.
- Optional: **Docker** if you prefer `docker-compose` instead of a local venv.

---

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in values.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQL store (`postgresql+psycopg://…` for Neon; `sslmode=require` in query string) |
| `NEON_DATABASE_URL` | Optional alias; backend accepts this instead of `DATABASE_URL` |
| `OPENROUTER_API_KEY` | LLM calls (coroner, synthesis) |
| `OPENROUTER_MODEL` | e.g. `openai/gpt-4o-mini` |
| `OPENROUTER_BASE_URL` | Default `https://openrouter.ai/api/v1` |
| `PINECONE_API_KEY` / `PINECONE_INDEX_NAME` / `PINECONE_ENVIRONMENT` | Vector index (serverless region) |
| `EMBEDDING_MODEL` | Default `BAAI/bge-base-en-v1.5` (local, no embedding API cost) |
| `EMBEDDING_DIM` | `768` for BGE base |
| `SECRET_KEY` | App secret for signing/hashing as implemented by the backend |
| `BACKEND_URL` | Used by clients pointing at this API (often `http://localhost:8000`) |

---

## Quick start

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r backend/requirements.txt
pip install -e ./sdk

cp backend/.env.example backend/.env
# Edit backend/.env with your keys and Neon URL

cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal (venv active), from the **repository root**:

```bash
python seed_data/seed.py --force
graveyard doctor --backend-url http://127.0.0.1:8000
graveyard recent --backend-url http://127.0.0.1:8000 --api-key community --limit 5
python scripts/verify_setup.py
```

**CLI detail:** `--backend-url` and `--json` work **either** before **or** after the subcommand (e.g. `graveyard doctor --backend-url http://127.0.0.1:8000` and `graveyard --backend-url http://127.0.0.1:8000 doctor` are both valid).

Docker alternative:

```bash
docker-compose up --build
```

---

## Verification checklist

Use this after any fresh clone or env change.

1. **Backend up:** `GET /health` returns `"status": "ok"` (database + Pinecone both passing).
2. **`graveyard doctor`** shows green checks; if **degraded**, fix Pinecone env vars; if **unhealthy**, fix `DATABASE_URL`.
3. **Seed:** `python seed_data/seed.py --force` so SQL + Pinecone have community examples.
4. **Data visible:** `graveyard recent --backend-url … --api-key community` lists rows.
5. **Wisdom:** `graveyard wisdom --backend-url … --api-key community --task "rate limit API"` should eventually show non-zero confidence once vectors exist and the query matches.
6. **Demos:** run scripts under `demo/` (see below).

Automated smoke test (backend must already be running):

```bash
python scripts/verify_setup.py --api-key community
```

Optional Makefile shortcuts (Git Bash / WSL / macOS): `make install-sdk`, `make seed`, `make verify`.

---

## Terminal CLI (`graveyard`)

Install the SDK (`pip install -e ./sdk`) to get the `graveyard` command.

| Command | Description |
|---------|-------------|
| `graveyard health` | Compact status + DB/Pinecone checks |
| `graveyard doctor` | Same as health plus remediation hints |
| `graveyard overview --api-key KEY` | Analytics JSON (pretty-printed) |
| `graveyard recent --api-key KEY` | Table of recent failures |
| `graveyard wisdom --api-key KEY --task "…"` | Wisdom panel + confidence |

Add `--json` for scripting (`graveyard --json health`).

---

## SDK usage (minimal)

After `pip install -e ./sdk`, import the package by name:

```python
from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

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
    return "ok"
```

More examples: `sdk/README.md` and `demo/*.py`.

---

## Demo scripts

| Script | What it exercises |
|--------|-------------------|
| `demo/demo_agent.py` | Wrapped agent + failure path |
| `demo/demo_success_only.py` | Success-only run |
| `demo/demo_failure_only.py` | Forces failure → coroner pipeline |
| `demo/demo_async_agent.py` | `watch_async` |
| `demo/demo_wisdom_query.py` | Direct wisdom API via client |

Run from repo root with venv active and `PYTHONPATH` including the repo (demos add the repo root to `sys.path` where needed).

---

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `confidence_score` 0 and empty `similar_failures` | No seed data or Pinecone mismatch; run seed script; confirm same embedding model/dimension as stored vectors |
| `graveyard` not found | Run `pip install -e ./sdk` inside your venv |
| `unrecognized arguments: --backend-url` | Reinstall the SDK (`pip install -e ./sdk`); older builds only accepted `--backend-url` before the subcommand |
| Postgres connection drops | Pool recycle/pre-ping are configured; check Neon idle timeouts and firewall |
| Wisdom slow first time | Local BGE model downloads on first embedding pass |

---

## Technologies

- Python (SDK + backend), FastAPI, LangGraph, SQLAlchemy, Pinecone, **local** `BAAI/bge-base-en-v1.5` embeddings (768-d), OpenRouter (LLM), Docker Compose, Rich (terminal).

---

## Features

- `GraveyardWrapper` decorator for automatic failure capture and reporting.
- LangGraph pipeline for structuring incidents; embeddings stored in Pinecone.
- Pre-task wisdom injection via semantic similarity.
- Community seed data for shared failure patterns.
- Rich terminal logging and the `graveyard` CLI.
- `GET /health` reports **database** and **Pinecone** status for operations and scripts.

---

## Process (design)

The SDK decorator was designed to be low-friction: wrap a function, and failures are sent to the backend without restructuring your agent. The backend turns raw traces into reusable patterns. Wisdom retrieval uses local embeddings to avoid paid embedding APIs on every request.

---

## What we learned

- Failure modes as structured data, not one-off logs.
- LangGraph as an enrichment pipeline (not only multi-agent orchestration).
- Local embeddings for latency and cost control on retrieval-heavy paths.
- Decorator-based SDK integration.

---

## Growth

Building Agent Graveyard emphasizes **reliability and memory** in agentic systems: not only what the model can do, but how it recovers and avoids repeating the same mistake.

---

## Optional: demo video

<!-- Attach your demo video here -->
