"""
Seed community failure memories for Agent Graveyard.

Aligned with current project setup:
- Local embeddings via `backend.memory.embeddings.generate_embedding` (BAAI/bge-base-en-v1.5)
- Pinecone vector upsert (best-effort)
- SQL persistence for backend API routes

Run from project root:
  python seed_data/seed.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure `backend.*` imports work when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from backend.db.database import Base, SessionLocal, engine
from backend.db.models import FailureMemory
from backend.memory.embeddings import generate_embedding
from backend.memory.pinecone_client import initialize_pinecone, upsert_failure_memory

load_dotenv()

SEED_DIR = Path(__file__).parent
SEED_FILES = [
    SEED_DIR / "common_langchain_failures.json",
    SEED_DIR / "common_api_failures.json",
    SEED_DIR / "common_failures.json",
]


def _seed_one_file(path: Path, force: bool = False) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    db = SessionLocal()
    count = 0

    for idx, row in enumerate(rows):
        failure_id = f"seed-{path.stem}-{idx}"

        # If not forcing, skip rows that already exist.
        existing = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
        if existing and not force:
            continue

        metadata = {
            "failure_reason": row["failure_reason"],
            "lesson": row["lesson"],
            "failure_category": row["failure_category"],
            "suggested_approach": row["suggested_approach"],
            "agent_name": row.get("agent_name", "community"),
            "is_community_shared": row.get("is_community_shared", True),
            "times_occurred": row.get("times_occurred", 1),
            "api_key_hash": "community",
        }

        # Best-effort Pinecone upsert: if Pinecone/config is unavailable,
        # SQL rows still get seeded so backend API remains usable.
        try:
            emb_text = f"{row['task_description']}\n{row['failure_reason']}"
            emb = generate_embedding(emb_text)
            upsert_failure_memory(failure_id=failure_id, embedding=emb, metadata=metadata)
        except Exception as exc:
            print(f"[warn] Pinecone upsert skipped for {failure_id}: {exc}")

        if existing:
            existing.task_description = row["task_description"]
            existing.agent_name = row.get("agent_name", "community")
            existing.failure_point = row.get("failure_point", "seed")
            existing.failure_reason = row["failure_reason"]
            existing.error_type = row["error_type"]
            existing.error_message = row.get("error_message", row["failure_reason"])
            existing.lesson = row["lesson"]
            existing.suggested_approach = row["suggested_approach"]
            existing.failure_category = row["failure_category"]
            existing.tools_attempted = row.get("tools_attempted", [])
            existing.what_was_tried = row.get("what_was_tried", row["suggested_approach"])
            existing.embedding_id = failure_id
            existing.times_occurred = row.get("times_occurred", 1)
            existing.resolved_eventually = bool(row.get("resolved_eventually", False))
            existing.self_heal_attempted = bool(row.get("self_heal_attempted", False))
            existing.self_heal_succeeded = bool(row.get("self_heal_succeeded", False))
            existing.api_key_hash = "community"
            existing.is_community_shared = bool(row.get("is_community_shared", True))
        else:
            db.add(
                FailureMemory(
                    id=failure_id,
                    task_description=row["task_description"],
                    failure_point=row.get("failure_point", "seed"),
                    failure_reason=row["failure_reason"],
                    error_type=row["error_type"],
                    error_message=row.get("error_message", row["failure_reason"]),
                    tools_attempted=row.get("tools_attempted", []),
                    what_was_tried=row.get("what_was_tried", row["suggested_approach"]),
                    lesson=row["lesson"],
                    suggested_approach=row["suggested_approach"],
                    failure_category=row["failure_category"],
                    embedding_id=failure_id,
                    times_occurred=row.get("times_occurred", 1),
                    resolved_eventually=bool(row.get("resolved_eventually", False)),
                    self_heal_attempted=bool(row.get("self_heal_attempted", False)),
                    self_heal_succeeded=bool(row.get("self_heal_succeeded", False)),
                    agent_name=row.get("agent_name", "community"),
                    api_key_hash="community",
                    is_community_shared=bool(row.get("is_community_shared", True)),
                )
            )

        count += 1

    db.commit()
    db.close()
    return count


def seed(force: bool = False) -> None:
    Base.metadata.create_all(bind=engine)

    try:
        initialize_pinecone()
    except Exception as exc:
        print(f"[warn] Pinecone init failed, proceeding with SQL-only seed: {exc}")

    total = 0
    for seed_file in [p for p in SEED_FILES if p.exists()]:
        if not seed_file.exists():
            print(f"[warn] Missing seed file: {seed_file}")
            continue
        inserted = _seed_one_file(seed_file, force=force)
        print(f"[seed] {seed_file.name}: {inserted} rows {'upserted' if force else 'inserted/skipped'}")
        total += inserted

    if total == 0 and not any(p.exists() for p in SEED_FILES):
        print("[warn] No seed JSON files found in seed_data/.")

    print(f"[done] Seed complete. Rows processed this run: {total}")


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
