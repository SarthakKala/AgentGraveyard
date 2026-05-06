# AgentGraveyard

*"Every agent that fails before yours already knew the answer. AgentGraveyard makes sure yours inherits it."*

AgentGraveyard is a self-healing failure memory system for AI agents. When your agent fails, a Coroner Agent diagnoses what went wrong, pulls lessons from similar past failures, and stores a synthesized strategy. The next agent running a similar task gets that knowledge handed to it before it even starts, not raw logs, but a distilled lesson it can actually use.

---

## 🛠️ Technologies

- Python + FastAPI (Backend)
- PostgreSQL via Neon (Structured storage)
- Pinecone (Vector search)
- sentence-transformers (Local embeddings — no paid API)
- OpenRouter (LLM for lesson synthesis)
- Python SDK with Rich terminal output
- Docker + Docker Compose

---

## ✨ Features

- Wrap any existing agent function with one decorator — nothing else in your code changes
- Before every task, the agent gets a wisdom briefing pulled from semantically similar past failures
- On failure, a Coroner Agent classifies what went wrong, retrieves similar incidents, and synthesizes a single actionable lesson
- Confidence scores are similarity-driven and they reflect actual retrieval quality, not made-up percentages
- CLI to query wisdom, inspect recent failures, and check system health
- Pre-seeded with hundreds of real AI agent failure patterns out of the box so new agents benefit from day one

---

## 🪦 The Problem Nobody Actually Fixes

Every AI agent tutorial shows you how to build one. None of them show you what happens when it fails. You debug it, fix it, move on and two weeks later a different agent makes the exact same mistake. Agent Graveyard fixes that. Persistent, semantic failure memory so agents stop starting from zero every time.

---

## 🔧 Process

The hard part wasn't storing failures, it was making them queryable in a way that actually helps. Every failure gets structured as a document with a task, error category, lesson, and suggested fix, then embedded as a vector. When a new failure comes in, the Coroner pulls the most similar past incidents, feeds them to an LLM, and stores one synthesized strategy. Future agents get that output and not a wall of raw logs.

The SDK wrapper was designed around a single constraint: add one decorator to a function you already have, and nothing else changes. The rest: wisdom query, event logging, Coroner trigger — happens entirely in the background. The caller never touches it.

The trickiest part was getting the synthesis prompt right. Multiple past failures often contradict each other: one says "retry immediately", another says "back off and wait". The prompt had to force the LLM to produce one coherent, actionable lesson from conflicting inputs consistently. That took significant iteration.

---

## 📚 What I Learned

- **Vector search for failure memory** — how to structure failure documents so semantic search retrieves the right past incidents, not just lexically similar ones
- **LLM synthesis prompts** — how to get consistent, actionable output from an LLM when the input is multiple conflicting past lessons
- **Python SDK design** — how to wrap existing sync and async functions transparently with one decorator, without the caller changing anything
- **FastAPI + SQLAlchemy** — building a real async backend with WebSocket broadcast, database sessions, and proper route separation
- **Retry logic for LLM APIs** — handling rate limits, backoff strategies, Retry-After headers, and surfacing clean errors when retries are exhausted

---

## 🌱 Overall Growth

This was the first project where I designed the entire intelligence layer myself, not just calling an API, but deciding how failures get stored, retrieved, classified, and turned into something useful. A raw database of errors is useless. The structure, the semantic search, and the synthesis step are what make it actually work. That distinction between storing data and making data actionable is something I'll carry into every AI system I build going forward.

---

## 🚀 Running the Project

You need free accounts at [Pinecone](https://pinecone.io), [OpenRouter](https://openrouter.ai), and [Neon](https://neon.tech).

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard

cp backend/.env.example backend/.env
# Fill in your Pinecone, OpenRouter, and Neon keys
```

**Linux / macOS / Git Bash:**
```bash
bash run.sh
```

**Windows PowerShell:**
```powershell
.\run.ps1
```

The script sets everything up and starts the backend on http://localhost:8000. The first run downloads a ~400MB embedding model once and caches it. Then in a second terminal:

```bash
source .venv/bin/activate
python demo/demo_agent.py
```

Full step-by-step setup: see [QUICKSTART.md](QUICKSTART.md)

---

## License

MIT — see [LICENSE](LICENSE)