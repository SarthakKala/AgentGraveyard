from functools import lru_cache
import os

from sentence_transformers import SentenceTransformer

EMBEDDING_DIM = 768


def _embed(text: str) -> list[float]:
    text = text.strip()
    if not text:
        return [0.0] * EMBEDDING_DIM
    vector = _get_model().encode(text, normalize_embeddings=True)
    return vector.tolist()


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    # Free local BGE model (downloads once, then cached on disk).
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    return SentenceTransformer(model_name)


def generate_embedding(text: str) -> list[float]:
    return _embed(text)


def generate_task_embedding(task_description: str) -> list[float]:
    return _embed(task_description)
