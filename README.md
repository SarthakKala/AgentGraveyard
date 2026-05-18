# AgentGraveyard

*"Every agent that fails before yours already knew the answer. AgentGraveyard makes sure yours inherits it."*

AgentGraveyard is a failure memory system for AI agents. When your agent fails, a Coroner Agent diagnoses what went wrong, pulls lessons from similar past failures, and stores a synthesized strategy. The next agent running a similar task can query that memory before it starts and get a distilled lesson to merge into its prompt. It does not automatically re-run your tools or fix the task for you.

---

## 🛠️ Technologies

- Python + FastAPI (Backend)
- LangGraph (Coroner pipeline orchestration)
- PostgreSQL via Neon or SQLite (Structured storage)
- Pinecone (Vector search)
- sentence-transformers (Local embeddings, no paid embedding API)
- OpenRouter (LLM for lesson synthesis)
- Python SDK with Rich terminal output
- Docker + Docker Compose

---

## ✨ Features

- Wrap any existing agent function with one decorator; wisdom and event logging run in the background
- Before every task, query similar past failures and receive a briefing via `get_wisdom_prompt_prefix()` (you merge that text into your agent prompt)
- On failure, a Coroner classifies the error, retrieves similar incidents, and synthesizes one actionable lesson (LangGraph pipeline)
- Confidence scores are similarity-driven (top match, average match, breadth), not a fixed percentage
- Optional `share_with_community=True` to store failures as community-visible lessons
- CLI (`graveyard`) to query wisdom, inspect recent failures, and check system health (pass the raw API key; the CLI hashes it)
- Pre-seeded with 100+ curated real agent failure patterns so new agents benefit from day one

---

## 🪦 The Problem Nobody Actually Fixes

Every AI agent tutorial shows you how to build one. None of them show you what happens when it fails. You debug it, fix it, move on, and two weeks later a different agent makes the exact same mistake. AgentGraveyard fixes that with persistent, semantic failure memory so agents stop starting from zero every time.

---

## 🔧 Process

The hard part was not storing failures. It was making them queryable in a way that actually helps. Every failure gets structured with a task, error category, lesson, and suggested fix, then embedded as a vector. When a new failure comes in, the Coroner (a LangGraph `StateGraph` over classify → diagnose → query → synthesize → store) pulls similar past incidents, feeds them to an LLM, and stores one synthesized strategy.

The SDK wrapper adds one decorator to a function you already have. The rest (wisdom query, event logging, coroner on failure) happens in the background. Sync `watch()` also works inside an existing `asyncio` event loop.

The trickiest part was the synthesis prompt. Multiple past failures often contradict each other. The prompt had to force the LLM to produce one coherent, actionable lesson from conflicting inputs consistently.

---

## 📚 What I Learned

- **Vector search for failure memory** — structuring failures so semantic search retrieves the right past incidents, not just lexically similar ones
- **LLM synthesis prompts** — consistent, actionable output when the input is multiple conflicting past lessons
- **LangGraph** — wiring the coroner as an explicit graph while keeping node logic testable
- **Python SDK design** — wrapping sync and async functions with one decorator, including safe HTTP from sync code inside running event loops
- **FastAPI + SQLAlchemy** — async backend with WebSocket broadcast, database sessions, and route separation
- **Retry logic for LLM APIs** — rate limits, backoff, `Retry-After`, and clear errors after retries are exhausted

---

## 🌱 Overall Growth

This was the first project where I designed the entire intelligence layer myself: how failures get stored, retrieved, classified, and turned into something useful. A raw database of errors is useless. The structure, semantic search, and synthesis step are what make it work. That distinction between storing data and making data actionable is something I will carry into every AI system I build going forward.

---

## 🚀 Running the Project

You need free accounts at [Pinecone](https://pinecone.io), [OpenRouter](https://openrouter.ai), and [Neon](https://neon.tech) (or use SQLite in `backend/.env` for local-only runs).

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard

cp backend/.env.example backend/.env
# Fill in your Pinecone, OpenRouter, and DATABASE_URL (Neon or SQLite)
```

**Linux / macOS / Git Bash:**
```bash
bash run.sh
```

**Windows PowerShell:**
```powershell
.\run.ps1
```

The script sets everything up and starts the backend on `http://localhost:8000` (open `http://localhost:8000/health` in your browser, not `0.0.0.0`). The first run downloads a ~400MB embedding model once. Then in a second terminal:

```bash
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
python demo/demo_e2e.py            # automated checks (recommended)
python demo/demo_agent.py          # full scrape failure + wisdom demo
```

Use the raw key `community` (or your registered key) with the SDK and CLI; hashing happens client-side.

Full step-by-step setup and all demo scripts: [QUICKSTART.md](QUICKSTART.md)

---

## License

MIT — see [LICENSE](LICENSE).
