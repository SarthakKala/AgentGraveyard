# AgentGraveyard

AgentGraveyard is a self-healing failure memory system for AI agents. The problem it solves is simple but annoying: production agents repeat the same failures over and over because they have no memory of what went wrong before. AgentGraveyard fixes that — it captures every failure your agent hits, synthesizes it into a structured incident, stores it in a vector database, and injects relevant warnings directly into the agent's prompt before future runs. Your agent learns from its own graveyard.

---

## 🛠️ Technologies

- Python (SDK + Backend)
- FastAPI (Backend API)
- LangGraph (Synthesis pipeline)
- SQLAlchemy (SQL memory store)
- Pinecone (Vector memory)
- BAAI/bge-base-en-v1.5 (Local embeddings, 768 dim)
- OpenRouter (LLM reasoning)
- Docker + Docker Compose
- Rich (Terminal CLI logs)

---

## ✨ Features

- `GraveyardWrapper` Python decorator — wrap any agent function and failure capture happens automatically, no manual logging needed
- Every captured failure is passed through a LangGraph synthesis pipeline that structures it into a reusable incident: what failed, why, and what to watch out for next time
- Pre-task wisdom injection — before any agent run, the system queries Pinecone by semantic similarity to the current task and prepends relevant past warnings directly into the prompt context
- Shared community memory — seed data pre-populates the graveyard with common agent failure patterns so new agents benefit from day one, not just after their own failures
- Terminal CLI with colored Rich logs: `health`, `overview`, `recent`, `wisdom` commands for visibility into the memory store without touching the API directly
- Full Docker Compose setup — one command brings up the entire backend stack
- SDK designed for drop-in integration — add `@graveyard.watch` to any existing agent function, nothing else changes

---

## 🪦 Agents Fail the Same Way, Over and Over — Until Now

The frustrating thing about agent failures is they're not random. Agents hit the same walls repeatedly — same tool call timing out, same prompt structure confusing the model, same edge case in the data. Every framework gives you logs. None of them give you memory. AgentGraveyard is that memory layer — a persistent, queryable, self-updating record of everything that's gone wrong, injected back into the agent before it tries again.

---

## 🔧 Process

The idea started from watching agents in development hit the same failure three times in a row during a single session. The logs were there but the agent had no way to use them. The fix needed to be invisible — you shouldn't have to restructure your agent to get failure memory, you should just wrap it.

The SDK decorator was the first piece. `@graveyard.watch` intercepts the function's execution, catches any exception, packages the task context and error into a structured payload, and ships it to the backend without the agent code knowing anything happened. That invisibility was the design constraint everything else was built around.

The backend synthesis pipeline uses LangGraph to turn raw error payloads into structured incidents. A raw exception trace is useless as memory — it's too specific. The pipeline extracts the general failure pattern: what class of task was being attempted, what went wrong at a conceptual level, and what a future agent should check before trying something similar. That structured output is what gets embedded and stored in Pinecone.

The wisdom injection was the hardest piece to get right. The query has to be semantic — you're not looking for the exact same task, you're looking for tasks similar enough that the past failure is relevant. Local BGE embeddings handle this without an API call, keeping latency low enough that the pre-task check doesn't noticeably slow down agent execution.

---

## 📚 What I Learned

- **AI agent reliability patterns** — how to think about failure modes in agentic systems as data, not just errors to catch and ignore
- **LangGraph for synthesis pipelines** — using LangGraph not for multi-agent orchestration but as a structured processing pipeline for transforming raw failure data into structured memory
- **Semantic retrieval with local embeddings** — running BAAI/bge-base-en-v1.5 locally for embedding generation so vector queries don't require an external API call on every agent run
- **Python SDK design** — building a decorator-based SDK that integrates invisibly into existing code without requiring any restructuring of the host application
- **Pinecone namespacing** — separating community shared memory from per-agent private memory using namespaces so both can be queried in the same retrieval call
- **Docker multi-service orchestration** — composing FastAPI backend, vector store client, and embedding model into a single `docker-compose up` stack

---

## 🌱 Overall Growth

AgentGraveyard pushed me to think about AI systems from a reliability and observability angle rather than just a capability angle. Most agent projects focus on what the agent can do. This one focuses on what happens when it can't — and how to make sure it doesn't fail the same way twice. That shift in perspective, from building features to building resilience, is something I'll carry into every agentic system I work on going forward.

---

## 🚀 Running the Project

```bash
git clone https://github.com/SarthakKala/AgentGraveyard.git
cd AgentGraveyard

# Start the backend
cd backend
python -m uvicorn main:app --reload --port 8000

# Seed shared community memory (from project root)
python seed_data/seed.py --force

# Use the SDK in your agent code
from sdk.agentgraveyard import GraveyardWrapper, get_wisdom_prompt_prefix

graveyard = GraveyardWrapper(
    api_key="your-api-key",
    backend_url="http://localhost:8000",
    verbose=True,
)

@graveyard.watch
def run_agent(task: str):
    wisdom = get_wisdom_prompt_prefix()
    if wisdom:
        print("Wisdom injected:\n", wisdom)
    # your agent logic here
    return "ok"
```

Or bring up the full stack with Docker:

```bash
docker-compose up --build
```

**Terminal CLI commands:**
```bash
graveyard health --backend-url http://localhost:8000
graveyard overview --backend-url http://localhost:8000 --api-key community
graveyard recent --backend-url http://localhost:8000 --api-key community --limit 10
graveyard wisdom --backend-url http://localhost:8000 --api-key community --task "scrape dynamic prices"
```

<!--

## 🎥 Video

Attach your demo video here -->