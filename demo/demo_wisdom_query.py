"""
Direct wisdom API demo — prints a readable summary (no raw JSON dump).

Run from repo root (backend on port 8000):
    python demo/demo_wisdom_query.py
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sdk"))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from agentgraveyard import GraveyardWrapper

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

TASK = "Scrape JS-heavy ecommerce site prices"


async def main() -> None:
    console = Console()
    graveyard = GraveyardWrapper(
        api_key="community",
        backend_url=BACKEND_URL,
        verbose=False,
    )

    console.print(Rule(title="Demo: direct wisdom query", style="bold"))
    console.print(f"[dim]Backend[/] {BACKEND_URL}")
    console.print(f"[dim]Task[/]     {TASK}\n")

    raw = await graveyard.query_wisdom(TASK)
    w = raw.get("wisdom") or {}

    has_warnings = bool(w.get("has_warnings"))
    confidence = float(w.get("confidence_score") or 0.0)
    similar = w.get("similar_failures") or []
    synthesized = (w.get("synthesized_recommendation") or "").strip()

    if not has_warnings:
        console.print(
            Panel(
                "[yellow]No wisdom above your similarity threshold.[/]\n"
                "Seed more failures, lower WISDOM_SIMILARITY_THRESHOLD in backend/.env, "
                "or try a broader task description.",
                title="Result",
            )
        )
        return

    console.print(
        f"[green]Warnings:[/] yes   "
        f"[green]Confidence:[/] {confidence:.0%}   "
        f"[green]Matches:[/] {len(similar)}"
    )
    console.print()

    console.print(Rule(title="Similar past failures (top signals)", style="dim"))
    for i, sf in enumerate(similar, 1):
        sid = str(sf.get("failure_id", ""))
        short_id = sid if len(sid) <= 36 else sid[:16] + "…"
        cat = sf.get("failure_category") or "?"
        sim = float(sf.get("similarity_score") or 0.0)
        lesson = (sf.get("lesson") or "").replace("\n", " ").strip()
        if len(lesson) > 160:
            lesson = lesson[:157] + "…"
        console.print(
            f"[bold]{i:>2}.[/] [{cat}]  similarity [cyan]{sim:.2f}[/]  [dim]{short_id}[/]"
        )
        console.print(f"    {lesson}")
        console.print()

    if synthesized:
        console.print(Rule(title="Synthesized recommendation (LLM)", style="dim"))
        console.print(Markdown(synthesized))
        console.print()

    prefix = (raw.get("prompt_prefix") or "").strip()
    if prefix:
        console.print(
            Panel(
                "[dim]This is the same text you would prepend via "
                "[bold]get_wisdom_prompt_prefix()[/] inside a wrapped agent. "
                "It duplicates the briefing above for prompt injection.[/]",
                title="About prompt_prefix",
                border_style="dim",
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
