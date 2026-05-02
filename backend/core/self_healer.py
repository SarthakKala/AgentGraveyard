import time
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.models import FailureMemory, SuccessMemory
from memory.pinecone_client import update_failure_metadata


class SelfHealResult(BaseModel):
    succeeded: bool
    approach_used: str
    execution_time_ms: int
    error_if_failed: str | None = None


async def attempt_self_heal(
    original_task: str,
    synthesized_solution: str,
    failure_id: str,
    agent_name: str,
    api_key_hash: str,
    db: Session,
) -> SelfHealResult:
    started = time.perf_counter()
    # Does NOT re-run user tools or verify the task — only records whether we had a non-empty strategy.
    succeeded = bool(synthesized_solution.strip())
    elapsed = int((time.perf_counter() - started) * 1000)
    failure = db.query(FailureMemory).filter(FailureMemory.id == failure_id).first()
    if failure is None:
        return SelfHealResult(
            succeeded=False,
            approach_used=synthesized_solution,
            execution_time_ms=elapsed,
            error_if_failed="failure memory not found",
        )
    failure.self_heal_attempted = True
    failure.self_heal_succeeded = succeeded
    if succeeded:
        failure.resolved_eventually = True
        failure.resolution_description = (
            "Recorded synthesized remediation text (heuristic). "
            "Does not prove the original agent task was re-executed successfully."
        )
        success = SuccessMemory(
            task_description=original_task,
            agent_name=agent_name,
            linked_failure_id=failure_id,
            wisdom_used=[failure_id],
            approach_used=synthesized_solution,
            execution_time_ms=elapsed,
            api_key_hash=api_key_hash,
        )
        db.add(success)
        update_failure_metadata(failure_id, {"resolved_eventually": True})
    db.commit()
    return SelfHealResult(
        succeeded=succeeded,
        approach_used=synthesized_solution,
        execution_time_ms=elapsed,
        error_if_failed=None if succeeded else "No synthesized remediation text to record",
    )
