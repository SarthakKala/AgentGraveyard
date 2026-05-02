from memory.schemas import SimilarFailure

from .llm_client import openrouter_chat


def _compute_confidence(similar_failures: list[SimilarFailure], *, llm_ok: bool) -> float:
    """
    Similarity-driven confidence:
      - top-1 similarity (main signal)
      - mean similarity across returned matches (corroboration)
      - breadth bonus for having several matches
      - small penalty when synthesis fell back to a bullet list
    """
    if not similar_failures:
        return 0.45

    scores = [float(sf.similarity_score) for sf in similar_failures[:5]]
    top = scores[0]
    avg = sum(scores) / len(scores)
    breadth = min(len(scores), 5) / 5.0

    base = 0.55 * top + 0.35 * avg + 0.10 * breadth
    if not llm_ok:
        base -= 0.05

    return round(min(0.97, max(0.30, base)), 2)


def synthesize_solution(similar_failures: list[SimilarFailure], fallback: str) -> tuple[str, float]:
    if not similar_failures:
        return fallback, _compute_confidence([], llm_ok=True)

    lessons = [
        f"- Lesson: {item.lesson} | Suggested: {item.suggested_approach}"
        for item in similar_failures[:3]
    ]
    try:
        recommendation = openrouter_chat(
            system_prompt="You synthesize robust agent remediation strategies.",
            user_prompt=(
                "Combine the following failure lessons into one concise, actionable strategy.\n"
                f"{chr(10).join(lessons)}"
            ),
            temperature=0.1,
        )
        return recommendation, _compute_confidence(similar_failures, llm_ok=True)
    except Exception:
        recommendation = "Combined strategy:\n" + "\n".join(lessons)
        return recommendation, _compute_confidence(similar_failures, llm_ok=False)
