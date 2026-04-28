from datetime import datetime

from pydantic import BaseModel, Field


class FailureMemoryCreate(BaseModel):
    task_description: str
    agent_name: str
    failure_point: str
    failure_reason: str
    error_type: str
    error_message: str
    tools_attempted: list[str] = Field(default_factory=list)
    what_was_tried: str
    api_key_hash: str
    is_community_shared: bool = False


class FailureMemoryResponse(BaseModel):
    id: str
    task_description: str
    agent_name: str
    failure_point: str
    failure_reason: str
    error_type: str
    lesson: str
    suggested_approach: str
    failure_category: str
    times_occurred: int
    resolved_eventually: bool
    self_heal_attempted: bool
    self_heal_succeeded: bool
    created_at: datetime


class SimilarFailure(BaseModel):
    failure_id: str
    similarity_score: float
    lesson: str
    suggested_approach: str
    failure_category: str
    times_occurred: int


class WisdomBriefing(BaseModel):
    has_warnings: bool
    similar_failures: list[SimilarFailure]
    synthesized_recommendation: str
    confidence_score: float


class SDKEvent(BaseModel):
    event_type: str
    session_id: str
    agent_name: str
    task_description: str
    api_key_hash: str
    timestamp: datetime
    payload: dict = Field(default_factory=dict)
