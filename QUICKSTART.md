# 🪦 Agent Graveyard — Quick Start

Get the full demo running in under 10 minutes.

---

## What You Need (all free)

| Service | Free Tier | Link |
|---|---|---|
| **Pinecone** | 1 free index, 100k vectors | https://pinecone.io → sign up → API Keys |
| **OpenRouter** | Free credits on signup | https://openrouter.ai → Dashboard → Keys |
| **Neon** (Postgres) | Free serverless Postgres | https://neon.tech → New Project → Connection String |

> **Note:** OpenRouter gives you access to free LLM models (we use `nvidia/nemotron-3-super-120b-a12b:free` by default — costs $0). Neon gives you a free Postgres database hosted in the cloud. Pinecone gives you a free vector index.

---

## Step 1 — Clone & Enter

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard
```

## Step 2 — Create Your Environment File

```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in these values:

```env
# From Pinecone dashboard → API Keys
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_INDEX_NAME=agent-graveyard
PINECONE_ENVIRONMENT=us-east-1

# From OpenRouter dashboard → API Keys
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# From Neon → your project → Connection Details → Connection string
# Use the psycopg format shown below
DATABASE_URL=postgresql+psycopg://user:password@host/dbname?sslmode=require

# Leave these as-is
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5
EMBEDDING_DIM=768
SECRET_KEY=change-this-to-any-random-string
```

## Step 3 — Run Setup (installs everything + seeds the database)

**Linux / macOS / Git Bash (Windows):**

```bash
bash run.sh
```

This will:

- Create a Python virtual environment
- Install all backend dependencies
- Install the SDK in editable mode
- Install demo dependencies (`requests`, `beautifulsoup4`)
- Run `scripts/check_env.py` (must pass)
- Seed Pinecone + database with community failures from `seed_data/common_failures.json`
- Start the backend server on http://localhost:8000

The script keeps the server running; **open a second terminal** for the next steps.

**Windows (PowerShell, no Git Bash):** from repo root:

```powershell
.\run.ps1
```

**First-time embedding download:** the seed step and the API load **`sentence-transformers`** and may download **~400MB** for `BAAI/bge-base-en-v1.5` into your Hugging Face cache. You will see `[embeddings] Loading embedding model...` on stderr; wait until it finishes (slow networks can take 10+ minutes). To hide that banner in CI, set `AGENT_GRAVEYARD_QUIET_EMBED=true`.

## Step 4 — Verify Everything Works

In a **new** terminal (repo root, venv activated):

```bash
source .venv/bin/activate   # Windows (Git Bash): source .venv/Scripts/activate
python scripts/check_env.py
```

You should see all green checkmarks. If anything is red, it will tell you exactly what to fix.

## Step 5 — Run The Demo

```bash
python demo/demo_agent.py
```

You will see the Agent Graveyard flow in your terminal (Rich-colored SDK logs when `verbose=True`).

---

## Using The CLI

Global flags can appear before or after the subcommand. Examples (community seed key):

```bash
graveyard --backend-url http://localhost:8000 health
graveyard doctor --backend-url http://localhost:8000
graveyard overview --backend-url http://localhost:8000 --api-key community
graveyard recent --backend-url http://localhost:8000 --api-key community --limit 10
graveyard wisdom --backend-url http://localhost:8000 --api-key community --task "scrape a React website"
```

## Using The SDK In Your Own Agent

Wisdom is only useful if you **merge it into your prompt**. Call `get_wisdom_prompt_prefix()` inside your agent and prepend it to the model input (or pass `task=` / `task_description=` so the wrapper queries wisdom for the right string).

```python
from agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(
    api_key="community",
    backend_url="http://localhost:8000",
    verbose=True,
)

@graveyard.watch
def my_agent(task: str) -> str:
    wisdom = get_wisdom_prompt_prefix()
    # your agent logic here
    ...

my_agent(task="scrape pricing data from an e-commerce site")
```

If your function has **multiple positional parameters**, pass the human-readable task explicitly: **`my_agent(..., task="...")`** or **`task_description="..."`**, or construct `GraveyardWrapper(..., task_param="my_kwarg_name")` so wisdom matches the correct keyword.

## Troubleshooting

**`ModuleNotFoundError: No module named 'agentgraveyard'`**  
→ Run `pip install -e ./sdk` from the repo root (with venv activated).

**`Connection refused` on port 8000**  
→ The backend is not running. Start it with `bash run.sh` or `cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`.

**`ERR_ADDRESS_INVALID` / “can’t reach” `http://0.0.0.0:8000`**  
→ **`0.0.0.0` is a bind/listen address for the server, not a URL you open in a browser.** Always use **`http://localhost:8000`** or **`http://127.0.0.1:8000`** (e.g. **`/health`**). `run.sh` / `run.ps1` listen on **`127.0.0.1`** so Uvicorn’s log matches that. Docker Compose still uses `0.0.0.0` inside the container; on your machine you still browse **`http://localhost:8000`**.

**`PineconeApiKeyError` / Pinecone errors**  
→ Check your `PINECONE_API_KEY` in `backend/.env`.

**Seed script hangs for a long time**  
→ First run downloads the embedding model (~400MB). Wait for it.

**`database is locked` (SQLite)**  
→ SQLite allows **one writer at a time**. Concurrent SDK calls (multiple HTTP handlers) can collide. Use **Neon/Postgres** for demos with concurrency, or run **uvicorn with a single worker** and avoid hammering the API from multiple clients.

**Neon SSL on Windows (`CERTIFICATE_VERIFY_FAILED`)**  
→ Ensure `DATABASE_URL` uses `?sslmode=require`. If it persists, install/OS certs may need updating; try Python from python.org (bundled certs) or add Neon’s guidance for Windows SSL to your environment.

**Pinecone upsert / dimension errors**  
→ Your index must match **`EMBEDDING_DIM`** (768 for BGE base). If you created `agent-graveyard` earlier with another dimension (e.g. 1536), **delete that index** in the Pinecone console or set **`PINECONE_INDEX_NAME`** to a new name.

**Low wisdom matches (`confidence_score` 0)**  
→ Raise **`WISDOM_SIMILARITY_THRESHOLD`** too strict? Default is **0.70**. Override in `backend/.env`: `WISDOM_SIMILARITY_THRESHOLD=0.55`. Seed data helps; cold starts may still show no match until similar failures exist.

**OpenRouter `429` / rate limits**  
→ Free tiers are strict; the backend retries a few times with backoff. Space out demo runs or use a paid model.

**`SSL connection error` on database**  
→ Make sure your `DATABASE_URL` includes `?sslmode=require` (required for Neon).

**`unrecognized arguments` from `graveyard`**  
→ Reinstall the SDK: `pip install -e ./sdk`. Use `graveyard --help` for the current CLI.
