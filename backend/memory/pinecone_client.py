import os
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

_pc: Pinecone | None = None
_index: Any = None


def initialize_pinecone() -> None:
    global _pc, _index
    if _index is not None:
        return
    api_key = os.getenv("PINECONE_API_KEY", "")
    index_name = os.getenv("PINECONE_INDEX_NAME", "agent-graveyard")
    region = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    embedding_dim = int(os.getenv("EMBEDDING_DIM", "768"))
    _pc = Pinecone(api_key=api_key)
    existing = {item["name"] for item in _pc.list_indexes()}
    if index_name not in existing:
        _pc.create_index(
            name=index_name,
            dimension=embedding_dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=region),
        )
    _index = _pc.Index(index_name)


def upsert_failure_memory(failure_id: str, embedding: list, metadata: dict) -> None:
    initialize_pinecone()
    _index.upsert(vectors=[{"id": failure_id, "values": embedding, "metadata": metadata}])


def query_similar_failures(
    query_embedding: list, top_k: int = 5, filter_shared: bool = False, api_key_hash: str | None = None
) -> list:
    initialize_pinecone()
    query_filter = None
    if filter_shared:
        query_filter = {"is_community_shared": True}
    elif api_key_hash:
        query_filter = {"$or": [{"api_key_hash": api_key_hash}, {"is_community_shared": True}]}
    result = _index.query(vector=query_embedding, top_k=top_k, include_metadata=True, filter=query_filter)
    return [{"id": m["id"], "score": float(m["score"]), "metadata": m.get("metadata", {})} for m in result.get("matches", [])]


def update_failure_metadata(failure_id: str, metadata_updates: dict) -> None:
    initialize_pinecone()
    _index.update(id=failure_id, set_metadata=metadata_updates)


def delete_failure(failure_id: str) -> None:
    initialize_pinecone()
    _index.delete(ids=[failure_id])
