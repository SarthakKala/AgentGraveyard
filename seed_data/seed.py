import json
from pathlib import Path

from dotenv import load_dotenv

from backend.memory.embeddings import generate_embedding
from backend.memory.pinecone_client import initialize_pinecone, upsert_failure_memory

load_dotenv()


def seed_file(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    count = 0
    for row in payload:
        content = f"{row['task_description']}\n{row['failure_reason']}"
        embedding = generate_embedding(content)
        failure_id = f"seed-{path.stem}-{count}"
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
        upsert_failure_memory(failure_id=failure_id, embedding=embedding, metadata=metadata)
        count += 1
    return count


if __name__ == "__main__":
    initialize_pinecone()
    base = Path(__file__).parent
    total = 0
    for source in [base / "common_langchain_failures.json", base / "common_api_failures.json"]:
        total += seed_file(source)
    print(f"Seeded {total} failures.")
