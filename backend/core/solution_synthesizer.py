from memory.schemas import SimilarFailure

from .llm_client import openrouter_chat

def synthesize_solution(similar_failures: list[SimilarFailure], fallback: str) -> tuple[str, float]:
    if not similar_failures:
        return fallback, 0.45
    lessons = [f"- Lesson: {item.lesson} | Suggested: {item.suggested_approach}" for item in similar_failures[:3]]
    try:
        recommendation = openrouter_chat(
            system_prompt="You synthesize robust agent remediation strategies.",
            user_prompt=(
                "Combine the following failure lessons into one concise, actionable strategy.\n"
                f"{chr(10).join(lessons)}"
            ),
            temperature=0.1,
        )
        confidence = min(0.97, 0.65 + (0.08 * len(similar_failures[:3])))
        return recommendation, confidence
    except Exception:
        recommendation = "Combined strategy:\n" + "\n".join(lessons)
        confidence = min(0.95, 0.55 + (0.1 * len(similar_failures[:3])))
        return recommendation, confidence
