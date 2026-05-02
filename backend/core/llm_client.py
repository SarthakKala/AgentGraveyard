import os
import time

import httpx

_MAX_ATTEMPTS = 4


def openrouter_chat(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    last_exc: BaseException | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=45.0)
            if response.status_code == 429:
                ra = response.headers.get("Retry-After")
                try:
                    wait_s = float(ra) if ra not in (None, "") else min(2.0**attempt, 45.0)
                except ValueError:
                    wait_s = min(2.0**attempt, 45.0)
                time.sleep(min(wait_s, 60.0))
                last_exc = RuntimeError(
                    f"OpenRouter rate limited (429); attempt {attempt + 1}/{_MAX_ATTEMPTS}"
                )
                continue
            if response.status_code >= 500:
                time.sleep(min(2.0**attempt, 15.0))
                last_exc = RuntimeError(f"OpenRouter HTTP {response.status_code}")
                continue
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(min(2.0**attempt, 15.0))
                continue
            raise RuntimeError(f"OpenRouter request failed after {_MAX_ATTEMPTS} attempts") from exc

    if last_exc:
        raise RuntimeError("OpenRouter chat failed after retries") from last_exc
    raise RuntimeError("OpenRouter chat failed")
