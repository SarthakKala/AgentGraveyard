from datetime import datetime
import hashlib
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.coroner_agent import run_coroner
from core.self_healer import attempt_self_heal
from core.wisdom_injector import format_wisdom_for_prompt, get_wisdom_briefing
from db.database import get_db
from db.models import AgentSession, SuccessMemory
from memory.schemas import SDKEvent

from ..websocket import broadcast_event

router = APIRouter(prefix="/api/sdk", tags=["sdk"])


class RegisterResponse(BaseModel):
    api_key: str
    api_key_hash: str


@router.post("/register", response_model=RegisterResponse)
def register_sdk_user() -> RegisterResponse:
    api_key = f"ag_{uuid.uuid4().hex}"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return RegisterResponse(api_key=api_key, api_key_hash=api_key_hash)


@router.get("/wisdom")
async def get_wisdom(task: str, api_key_hash: str):
    wisdom = await get_wisdom_briefing(task_description=task, api_key_hash=api_key_hash)
    return {"wisdom": wisdom.model_dump(), "prompt_prefix": format_wisdom_for_prompt(wisdom)}


@router.post("/event")
async def ingest_event(event: SDKEvent, db: Session = Depends(get_db)):
    if event.event_type == "TASK_START":
        session = AgentSession(
            id=event.session_id,
            agent_name=event.agent_name,
            task_description=event.task_description,
            status="RUNNING",
            api_key_hash=event.api_key_hash,
        )
        db.merge(session)
        db.commit()
        await broadcast_event(
            event.api_key_hash,
            {"event_type": "AGENT_STARTED", "session_id": event.session_id, "agent_name": event.agent_name},
        )
    elif event.event_type == "TASK_SUCCESS":
        success = SuccessMemory(
            task_description=event.task_description,
            agent_name=event.agent_name,
            approach_used=event.payload.get("approach_used", ""),
            execution_time_ms=int(event.payload.get("execution_time_ms", 0)),
            api_key_hash=event.api_key_hash,
        )
        db.add(success)
        session = db.query(AgentSession).filter(AgentSession.id == event.session_id).first()
        if session:
            session.status = "SUCCESS"
            session.ended_at = datetime.utcnow()
        db.commit()
        await broadcast_event(event.api_key_hash, {"event_type": "AGENT_SUCCEEDED", "session_id": event.session_id})
    elif event.event_type == "TASK_FAILURE":
        state = await run_coroner(
            task_description=event.task_description,
            error_message=event.payload.get("error_message", ""),
            error_type=event.payload.get("error_type", "UnknownError"),
            tools_attempted=event.payload.get("tools_attempted", []),
            agent_name=event.agent_name,
            api_key_hash=event.api_key_hash,
            db=db,
        )
        heal = await attempt_self_heal(
            original_task=event.task_description,
            synthesized_solution=state.get("synthesized_solution", ""),
            failure_id=state["failure_id"],
            agent_name=event.agent_name,
            api_key_hash=event.api_key_hash,
            db=db,
        )
        await broadcast_event(
            event.api_key_hash,
            {
                "event_type": "CORONER_COMPLETE",
                "session_id": event.session_id,
                "failure_id": state["failure_id"],
                "self_heal_succeeded": heal.succeeded,
            },
        )
    return {"ok": True}
