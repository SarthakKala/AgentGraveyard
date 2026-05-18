import hashlib


def api_key_hash(raw_key: str) -> str:
    return hashlib.sha256(raw_key.strip().encode()).hexdigest()
