import os

from memory.embeddings import generate_task_embedding
from memory.pinecone_client import query_similar_failures
from memory.schemas import SimilarFailure, WisdomBriefing

from .solution_synthesizer import synthesize_solution


def _similarity_threshold() -> float:
    raw = os.getenv("WISDOM_SIMILARITY_THRESHOLD", "0.70").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.70


async def get_wisdom_briefing(
    task_description: str, api_key_hash: str, include_community: bool = True
) -> WisdomBriefing:
    task_embedding = generate_task_embedding(task_description)
    matches = query_similar_failures(
        task_embedding,
        top_k=5,
        filter_shared=not include_community and not api_key_hash,
        api_key_hash=api_key_hash,
    )
    similar_failures: list[SimilarFailure] = []
    for match in matches:
        md = match.get("metadata", {})
        similar_failures.append(
            SimilarFailure(
                failure_id=match["id"],
                similarity_score=match["score"],
                lesson=md.get("lesson", ""),
                suggested_approach=md.get("suggested_approach", ""),
                failure_category=md.get("failure_category", "REASONING_FAILURE"),
                times_occurred=int(md.get("times_occurred", 1)),
            )
        )
    threshold = _similarity_threshold()
    if not similar_failures or similar_failures[0].similarity_score < threshold:
        top = similar_failures[0].similarity_score if similar_failures else None
        hint = (
            f"No matches above similarity threshold ({threshold:.2f}). "
            "Seed more data, lower WISDOM_SIMILARITY_THRESHOLD in backend/.env, or broaden the task text."
        )
        if top is not None:
            hint += f" Best match score was {top:.2f}."
        return WisdomBriefing(
            has_warnings=False,
            similar_failures=[],
            synthesized_recommendation=hint,
            confidence_score=0.0,
        )
    recommendation, confidence = synthesize_solution(similar_failures, "Proceed carefully with retries and validation.")
    return WisdomBriefing(
        has_warnings=True,
        similar_failures=similar_failures,
        synthesized_recommendation=recommendation,
        confidence_score=confidence,
    )


def format_wisdom_for_prompt(wisdom: WisdomBriefing) -> str:
    if not wisdom.has_warnings:
        return ""
    lines = [
        "AGENT GRAVEYARD WISDOM BRIEFING",
        f"{len(wisdom.similar_failures)} similar past failures detected.",
        "",
    ]
    for idx, sf in enumerate(wisdom.similar_failures, start=1):
        lines.append(
            f"{idx}. [{sf.failure_category}, similarity: {sf.similarity_score:.2f}] Lesson: {sf.lesson}\n"
            f"   Suggested: {sf.suggested_approach}"
        )
    lines.append("")
    lines.append(f"SYNTHESIZED RECOMMENDATION (confidence: {wisdom.confidence_score:.2f})")
    lines.append(wisdom.synthesized_recommendation)
    return "\n".join(lines)
