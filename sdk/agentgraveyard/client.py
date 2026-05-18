from datetime import datetime, timezone
from typing import Any
import uuid

import httpx

from .identity import api_key_hash as hash_api_key


class GraveyardClient:
    def __init__(self, api_key: str, backend_url: str):
        self.api_key = api_key
        self.backend_url = backend_url.rstrip("/")
        self.api_key_hash = hash_api_key(api_key)

    async def query_wisdom(self, task_description: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.backend_url}/api/sdk/wisdom",
                params={"task": task_description, "api_key_hash": self.api_key_hash},
            )
            response.raise_for_status()
            return response.json()

    async def send_event(self, event_type: str, agent_name: str, task_description: str, payload: dict[str, Any]) -> dict:
        body = {
            "event_type": event_type,
            "session_id": payload.get("session_id", str(uuid.uuid4())),
            "agent_name": agent_name,
            "task_description": task_description,
            "api_key_hash": self.api_key_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.backend_url}/api/sdk/event", json=body)
            response.raise_for_status()
            return response.json()
