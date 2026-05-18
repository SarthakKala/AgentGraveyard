import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.time_util import utc_now

from .database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class FailureMemory(Base):
    __tablename__ = "failure_memories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    failure_point: Mapped[str] = mapped_column(String, nullable=False)
    failure_reason: Mapped[str] = mapped_column(Text, nullable=False)
    error_type: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    tools_attempted: Mapped[list] = mapped_column(JSON, default=list)
    what_was_tried: Mapped[str] = mapped_column(Text, nullable=False, default="")
    lesson: Mapped[str] = mapped_column(Text, nullable=False, default="")
    suggested_approach: Mapped[str] = mapped_column(Text, nullable=False, default="")
    failure_category: Mapped[str] = mapped_column(String, nullable=False, default="REASONING_FAILURE")
    embedding_id: Mapped[str] = mapped_column(String, nullable=False)
    times_occurred: Mapped[int] = mapped_column(Integer, default=1)
    resolved_eventually: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    self_heal_attempted: Mapped[bool] = mapped_column(Boolean, default=False)
    self_heal_succeeded: Mapped[bool] = mapped_column(Boolean, default=False)
    agent_name: Mapped[str] = mapped_column(String, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_community_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class SuccessMemory(Base):
    __tablename__ = "success_memories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[str] = mapped_column(String, nullable=False)
    linked_failure_id: Mapped[str | None] = mapped_column(String, nullable=True)
    wisdom_used: Mapped[list] = mapped_column(JSON, default=list)
    approach_used: Mapped[str] = mapped_column(Text, default="")
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    api_key_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    agent_name: Mapped[str] = mapped_column(String, nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="RUNNING")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    api_key_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    failure_id: Mapped[str | None] = mapped_column(String, nullable=True)
    success_id: Mapped[str | None] = mapped_column(String, nullable=True)
