"""
Seed community failure memories for Agent Graveyard.

Aligned with current project setup:
- Local embeddings via `backend.memory.embeddings.generate_embedding` (BAAI/bge-base-en-v1.5)
- Pinecone vector upsert (best-effort)
- SQL persistence for backend API routes

Primary dataset: `seed_data/common_failures.json` (array of failure objects).
Optional extra fields per row: `source_citations` (list of URL strings) — stored in
vector metadata and used to enrich the embedding text.

Run from project root:
  python seed_data/seed.py
  python seed_data/seed.py --force
  python seed_data/seed.py --force --only common_failures.json
"""

from __future__ import annotations

import argparse
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
# Process in order; missing files are skipped. Put your main pack first.
SEED_FILES = [
    SEED_DIR / "common_failures.json",
    SEED_DIR / "common_langchain_failures.json",
    SEED_DIR / "common_api_failures.json",
]

# Pinecone metadata values are best kept short and string-friendly.
_MAX_META_SOURCES_LEN = 1900
_PROGRESS_WIDTH = 26


def _task_preview(row: dict, max_len: int = 42) -> str:
    t = (row.get("task_description") or row.get("failure_reason") or "?")[: max_len * 2]
    t = t.replace("\n", " ")
    if len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def _print_progress(file_name: str, index: int, total: int, status: str) -> None:
    """Single-line live progress (use print() after errors so the next line is clean)."""
    n = max(total, 1)
    filled = int(_PROGRESS_WIDTH * index / n)
    bar = "█" * filled + "░" * (_PROGRESS_WIDTH - filled)
    line = f"[seed] {file_name}  [{bar}]  {index:>4}/{total}  {status}"
    if len(line) > 118:
        line = line[:115] + "…"
    print(f"\r{line:<118}", end="", flush=True)


def _sources_blob(row: dict) -> str:
    cites = row.get("source_citations")
    if not cites:
        return ""
    if isinstance(cites, list):
        return " | ".join(str(c) for c in cites if c)[:_MAX_META_SOURCES_LEN]
    return str(cites)[:_MAX_META_SOURCES_LEN]


def _embedding_text(row: dict) -> str:
    parts = [row["task_description"], row["failure_reason"], row.get("lesson", "")]
    src = _sources_blob(row)
    if src:
        parts.append(src[:800])
    return "\n".join(p for p in parts if p)


def _pinecone_metadata(row: dict, failure_id: str) -> dict:
    meta = {
        "failure_reason": row["failure_reason"],
        "lesson": row["lesson"],
        "failure_category": row["failure_category"],
        "suggested_approach": row["suggested_approach"],
        "agent_name": row.get("agent_name", "community"),
        "is_community_shared": row.get("is_community_shared", True),
        "times_occurred": row.get("times_occurred", 1),
        "api_key_hash": "community",
        "failure_id": failure_id,
    }
    sources = _sources_blob(row)
    if sources:
        meta["sources"] = sources
    return meta


def _seed_one_file(path: Path, force: bool = False) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"{path.name} must be a JSON array")

    total = len(rows)
    print(f"[seed] Starting {path.name} — {total} row(s). This may take a while (embeddings + DB).")

    db = SessionLocal()
    count = 0

    for idx, row in enumerate(rows):
        failure_id = f"seed-{path.stem}-{idx}"
        cur = idx + 1
        _print_progress(path.name, cur, total, "scan")

        try:
            # Required keys for SQL + vectors
            required = (
                "task_description",
                "failure_reason",
                "error_type",
                "failure_category",
                "lesson",
                "suggested_approach",
            )
            missing = [k for k in required if k not in row]
            if missing:
                print()
                print(f"[skip] {failure_id}: missing keys {missing}")
                continue

            existing = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
            if existing and not force:
                _print_progress(path.name, cur, total, "skip (already seeded; use --force)")
                continue

            preview = _task_preview(row)
            _print_progress(path.name, cur, total, f"embed · {preview}")

            metadata = _pinecone_metadata(row, failure_id)

            try:
                emb = generate_embedding(_embedding_text(row))
                _print_progress(path.name, cur, total, f"vector · {preview}")
                upsert_failure_memory(failure_id=failure_id, embedding=emb, metadata=metadata)
            except Exception as exc:
                print()
                print(f"[warn] Pinecone upsert skipped for {failure_id}: {exc}")

            err_msg = row.get("error_message", row["failure_reason"])
            tools = row.get("tools_attempted") or []
            if not isinstance(tools, list):
                tools = [str(tools)]
            tried = row.get("what_was_tried") or row["suggested_approach"]

            if existing:
                existing.task_description = row["task_description"]
                existing.agent_name = row.get("agent_name", "community")
                existing.failure_point = row.get("failure_point", "seed")
                existing.failure_reason = row["failure_reason"]
                existing.error_type = row["error_type"]
                existing.error_message = err_msg
                existing.lesson = row["lesson"]
                existing.suggested_approach = row["suggested_approach"]
                existing.failure_category = row["failure_category"]
                existing.tools_attempted = tools
                existing.what_was_tried = tried
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
                        error_message=err_msg,
                        tools_attempted=tools,
                        what_was_tried=tried,
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
            _print_progress(path.name, cur, total, f"done · {preview}")
        except Exception as exc:
            print()
            print(f"[error] {failure_id}: {exc}")
            continue

    print()
    db.commit()
    db.close()
    return count


def seed(force: bool = False, only: str | None = None) -> None:
    Base.metadata.create_all(bind=engine)

    try:
        initialize_pinecone()
    except Exception as exc:
        print(f"[warn] Pinecone init failed, proceeding with SQL-only seed: {exc}")

    files: list[Path]
    if only:
        path = SEED_DIR / only
        if not path.is_file():
            print(f"[error] Seed file not found: {path}")
            return
        files = [path]
    else:
        files = [p for p in SEED_FILES if p.exists()]

    if not files:
        print("[warn] No seed JSON files found in seed_data/. Expected at least common_failures.json")
        return

    total = 0
    for seed_file in files:
        inserted = _seed_one_file(seed_file, force=force)
        print(f"[seed] {seed_file.name}: {inserted} rows {'upserted' if force else 'inserted/skipped'}")
        total += inserted

    print(f"[done] Seed complete. Rows processed this run: {total}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed failure memories from JSON packs.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update rows even if they already exist (same seed id)",
    )
    parser.add_argument(
        "--only",
        metavar="FILENAME",
        help="Seed only this file inside seed_data/ (e.g. common_failures.json)",
    )
    args = parser.parse_args()
    seed(force=args.force, only=args.only)


if __name__ == "__main__":
    main()
