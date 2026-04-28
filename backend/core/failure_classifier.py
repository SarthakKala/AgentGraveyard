from typing import Literal


FailureCategory = Literal[
    "TOOL_FAILURE",
    "PROMPT_FAILURE",
    "DATA_FAILURE",
    "ENVIRONMENT_FAILURE",
    "REASONING_FAILURE",
]


def classify_failure(error_type: str, error_message: str) -> FailureCategory:
    payload = f"{error_type} {error_message}".lower()
    if any(token in payload for token in ["timeout", "rate limit", "http", "connection"]):
        return "TOOL_FAILURE"
    if any(token in payload for token in ["parse", "json", "schema", "format"]):
        return "DATA_FAILURE"
    if any(token in payload for token in ["api key", "auth", "permission", "env"]):
        return "ENVIRONMENT_FAILURE"
    if any(token in payload for token in ["prompt", "instruction", "misunderstood"]):
        return "PROMPT_FAILURE"
    return "REASONING_FAILURE"
