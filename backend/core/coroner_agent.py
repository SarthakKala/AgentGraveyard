import uuid
from typing import TypedDict

from sqlalchemy.orm import Session

from db.models import FailureMemory
from memory.embeddings import generate_embedding
from memory.pinecone_client import query_similar_failures, upsert_failure_memory
from memory.schemas import SimilarFailure

from .failure_classifier import classify_failure
from .llm_client import openrouter_chat
from .solution_synthesizer import synthesize_solution


class CornerState(TypedDict, total=False):
    task_description: str
    error_message: str
    error_type: str
    tools_attempted: list[str]
    agent_name: str
    api_key_hash: str
    share_with_community: bool
    failure_category: str
    failure_reason: str
    failure_point: str
    what_was_tried: str
    lesson: str
    suggested_approach: str
    similar_failures: list[dict]
    synthesized_solution: str
    confidence_score: float
    failure_id: str


def classify_failure_node(state: CornerState) -> CornerState:
    state["failure_category"] = classify_failure(state["error_type"], state["error_message"])
    return state


def diagnose_failure_node(state: CornerState) -> CornerState:
    state["failure_point"] = state["tools_attempted"][-1] if state["tools_attempted"] else "agent_execution"
    state["failure_reason"] = state["error_message"]
    state["what_was_tried"] = ", ".join(state["tools_attempted"]) or "No tools logged"
    try:
        output = openrouter_chat(
            system_prompt="You are an AI coroner for agent failures. Be concrete and concise.",
            user_prompt=(
                f"Task: {state['task_description']}\n"
                f"Error type: {state['error_type']}\n"
                f"Error message: {state['error_message']}\n"
                f"Tools attempted: {state['tools_attempted']}\n\n"
                "Return two lines:\n"
                "LESSON: <short lesson>\n"
                "SUGGESTED_APPROACH: <concrete approach>"
            ),
            temperature=0.1,
        )
        lesson = next((line.replace("LESSON:", "").strip() for line in output.splitlines() if line.startswith("LESSON:")), "")
        suggested = next(
            (line.replace("SUGGESTED_APPROACH:", "").strip() for line in output.splitlines() if line.startswith("SUGGESTED_APPROACH:")),
            "",
        )
        state["lesson"] = lesson or f"Avoid repeating {state['error_type']} by validating assumptions earlier."
        state["suggested_approach"] = suggested or "Use retries, stronger validation, and alternate tool selection."
    except Exception:
        state["lesson"] = f"Avoid repeating {state['error_type']} by validating assumptions earlier."
        state["suggested_approach"] = "Use retries, stronger validation, and alternate tool selection."
    return state


def query_graveyard_node(state: CornerState) -> CornerState:
    emb = generate_embedding(f"{state['task_description']}\n{state['failure_reason']}")
    matches = query_similar_failures(emb, top_k=5, api_key_hash=state["api_key_hash"])
    state["similar_failures"] = matches
    return state


def synthesize_solution_node(state: CornerState) -> CornerState:
    normalized = []
    for item in state.get("similar_failures", [])[:3]:
        md = item.get("metadata", {})
        normalized.append(
            SimilarFailure(
                failure_id=item["id"],
                similarity_score=float(item["score"]),
                lesson=md.get("lesson", ""),
                suggested_approach=md.get("suggested_approach", ""),
                failure_category=md.get("failure_category", "REASONING_FAILURE"),
                times_occurred=int(md.get("times_occurred", 1)),
            )
        )
    synthesis, confidence = synthesize_solution(normalized, state["suggested_approach"])
    state["synthesized_solution"] = synthesis
    state["confidence_score"] = confidence
    return state


def store_failure_node(state: CornerState, db: Session) -> CornerState:
    failure_id = str(uuid.uuid4())
    embedding = generate_embedding(f"{state['task_description']}\n{state['failure_reason']}")
    community_shared = bool(state.get("share_with_community", False))
    metadata = {
        "failure_reason": state["failure_reason"],
        "lesson": state["lesson"],
        "failure_category": state["failure_category"],
        "suggested_approach": state["suggested_approach"],
        "agent_name": state["agent_name"],
        "api_key_hash": state["api_key_hash"],
        "is_community_shared": community_shared,
        "times_occurred": 1,
    }
    upsert_failure_memory(failure_id=failure_id, embedding=embedding, metadata=metadata)
    failure = FailureMemory(
        id=failure_id,
        task_description=state["task_description"],
        failure_point=state["failure_point"],
        failure_reason=state["failure_reason"],
        error_type=state["error_type"],
        error_message=state["error_message"],
        tools_attempted=state["tools_attempted"],
        what_was_tried=state["what_was_tried"],
        lesson=state["lesson"],
        suggested_approach=state["suggested_approach"],
        failure_category=state["failure_category"],
        embedding_id=failure_id,
        agent_name=state["agent_name"],
        api_key_hash=state["api_key_hash"],
        is_community_shared=community_shared,
    )
    db.add(failure)
    db.commit()
    state["failure_id"] = failure_id
    return state


async def run_coroner(
    task_description: str,
    error_message: str,
    error_type: str,
    tools_attempted: list[str],
    agent_name: str,
    api_key_hash: str,
    db: Session,
    share_with_community: bool = False,
) -> CornerState:
    from agents.graph import build_agent_graph

    initial: CornerState = {
        "task_description": task_description,
        "error_message": error_message,
        "error_type": error_type,
        "tools_attempted": tools_attempted,
        "agent_name": agent_name,
        "api_key_hash": api_key_hash,
        "share_with_community": share_with_community,
    }
    graph = build_agent_graph(db)
    return graph.invoke(initial)
