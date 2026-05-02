import os
from typing import Any

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

_pc: Pinecone | None = None
_index: Any = None


def _index_names(pc: Pinecone) -> set[str]:
    """Support multiple pinecone-client list_indexes response shapes."""
    try:
        lst = pc.list_indexes()
    except Exception:
        return set()
    names: set[str] = set()
    indexes = getattr(lst, "indexes", None)
    if indexes is not None:
        for item in indexes:
            n = getattr(item, "name", None)
            if n is None and isinstance(item, dict):
                n = item.get("name")
            if n:
                names.add(str(n))
        return names
    if isinstance(lst, (list, tuple)):
        for item in lst:
            if isinstance(item, dict) and "name" in item:
                names.add(str(item["name"]))
    return names


def _validate_existing_index_dimension(pc: Pinecone, index_name: str, expected_dim: int) -> None:
    try:
        lst = pc.list_indexes()
        indexes = getattr(lst, "indexes", None) or []
        for item in indexes:
            name = getattr(item, "name", None) or (item.get("name") if isinstance(item, dict) else None)
            if name != index_name:
                continue
            dim = getattr(item, "dimension", None)
            if dim is None and isinstance(item, dict):
                dim = item.get("dimension")
            if dim is not None and int(dim) != int(expected_dim):
                raise RuntimeError(
                    f"Pinecone index {index_name!r} has dimension {dim}, but EMBEDDING_DIM is {expected_dim}. "
                    "Delete the index in the Pinecone console or set PINECONE_INDEX_NAME to a new name."
                )
    except RuntimeError:
        raise
    except Exception:
        pass


def initialize_pinecone() -> None:
    global _pc, _index
    if _index is not None:
        return
    api_key = os.getenv("PINECONE_API_KEY", "")
    index_name = os.getenv("PINECONE_INDEX_NAME", "agent-graveyard")
    region = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    embedding_dim = int(os.getenv("EMBEDDING_DIM", "768"))
    _pc = Pinecone(api_key=api_key)
    existing = _index_names(_pc)
    if index_name not in existing:
        _pc.create_index(
            name=index_name,
            dimension=embedding_dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=region),
        )
    else:
        _validate_existing_index_dimension(_pc, index_name, embedding_dim)
    _index = _pc.Index(index_name)


def upsert_failure_memory(failure_id: str, embedding: list, metadata: dict) -> None:
    initialize_pinecone()
    expected = int(os.getenv("EMBEDDING_DIM", "768"))
    if len(embedding) != expected:
        raise RuntimeError(
            f"Embedding length {len(embedding)} does not match EMBEDDING_DIM={expected}. "
            "Fix your embedding model or EMBEDDING_DIM in backend/.env."
        )
    try:
        _index.upsert(vectors=[{"id": failure_id, "values": embedding, "metadata": metadata}])
    except Exception as exc:
        err = str(exc).lower()
        if "dimension" in err or "does not match" in err or "vector dimension" in err:
            raise RuntimeError(
                f"Pinecone rejected the vector (dimension mismatch). "
                f"Index must use dimension {expected} (same as EMBEDDING_DIM). "
                f"Delete index {os.getenv('PINECONE_INDEX_NAME', 'agent-graveyard')!r} or choose a new PINECONE_INDEX_NAME."
            ) from exc
        raise


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


def pinecone_health_check() -> dict[str, Any]:
    """Lightweight connectivity check for /health (after startup, index should exist)."""
    api_key = os.getenv("PINECONE_API_KEY", "").strip()
    if not api_key:
        return {"ok": False, "detail": "PINECONE_API_KEY is not set"}
    try:
        initialize_pinecone()
        if _index is None:
            return {"ok": False, "detail": "Pinecone index not initialized"}
        _index.describe_index_stats()
        return {"ok": True, "detail": None}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}
