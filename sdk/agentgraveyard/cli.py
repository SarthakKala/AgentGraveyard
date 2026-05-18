import argparse
import json
from typing import Any, Optional

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .identity import api_key_hash


def _api(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def _emit_json(data: Any) -> int:
    print(json.dumps(data, indent=2))
    return 0


def _fetch_health(backend_url: str) -> tuple[Optional[dict[str, Any]], Optional[BaseException]]:
    try:
        r = httpx.get(_api(backend_url, "/health"), timeout=15.0)
        r.raise_for_status()
        return r.json(), None
    except Exception as exc:
        return None, exc


def _render_health_payload(payload: dict[str, Any], args: argparse.Namespace) -> int:
    if args.json:
        return _emit_json(payload)

    console = Console(stderr=False)
    status = payload.get("status", "?")
    ver = payload.get("version", "?")
    style = "green" if status == "ok" else ("yellow" if status == "degraded" else "red")
    console.print(
        Panel.fit(f"[bold]{status.upper()}[/bold]  ·  API v{ver}", title="Agent Graveyard", border_style=style)
    )
    checks = payload.get("checks") or {}
    for name, row in checks.items():
        ok = row.get("ok")
        detail = row.get("detail")
        mark = "[green]OK[/green]" if ok else "[red]NO[/red]"
        line = f"{mark}  [bold]{name}[/bold]"
        if detail:
            line += f" — [dim]{detail}[/dim]"
        console.print(line)
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    payload, err = _fetch_health(args.backend_url)
    if err is not None or payload is None:
        _print_error("health check failed", err or RuntimeError("unknown"), args)
        return 1
    return _render_health_payload(payload, args)


def cmd_doctor(args: argparse.Namespace) -> int:
    """Run health and print remediation hints for common failure modes."""
    payload, err = _fetch_health(args.backend_url)
    if err is not None or payload is None:
        _print_error("health check failed", err or RuntimeError("unknown"), args)
        if not args.json:
            console = Console(stderr=True)
            console.print(
                "[yellow]Backend unreachable.[/yellow] Start it with: [bold]cd backend && python -m uvicorn main:app --reload --port 8000[/bold]"
            )
        return 1

    rc = _render_health_payload(payload, args)
    if args.json:
        return rc

    console = Console(stderr=True)
    checks = payload.get("checks") or {}
    pc = checks.get("pinecone") or {}
    if not pc.get("ok"):
        console.print(
            "\n[dim]Pinecone:[/dim] Set [bold]PINECONE_API_KEY[/bold], [bold]PINECONE_INDEX_NAME[/bold], and "
            "[bold]PINECONE_ENVIRONMENT[/bold] in [bold]backend/.env[/bold]. Wisdom retrieval needs a working index."
        )
    db = checks.get("database") or {}
    if not db.get("ok"):
        console.print(
            "\n[dim]Database:[/dim] Check [bold]DATABASE_URL[/bold] (or [bold]NEON_DATABASE_URL[/bold]) in [bold]backend/.env[/bold]. "
            "For Neon, use [bold]postgresql+psycopg://[/bold] and [bold]sslmode=require[/bold]."
        )
    if payload.get("status") == "ok":
        console.print(
            "\n[green]All checks passed.[/green] Run [bold]python seed_data/seed.py --force[/bold] "
            "if lists or wisdom look empty."
        )
    return 0


def cmd_overview(args: argparse.Namespace) -> int:
    key_hash = api_key_hash(args.api_key)
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/analytics/overview"),
            params={"api_key_hash": key_hash},
            timeout=20.0,
        )
        r.raise_for_status()
    except Exception as exc:
        _print_error("overview failed", exc, args)
        return 1
    payload = r.json()
    if args.json:
        return _emit_json(payload)

    console = Console()
    console.print(Panel(json.dumps(payload, indent=2), title="Overview", border_style="cyan"))
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    key_hash = api_key_hash(args.api_key)
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/failures"),
            params={"api_key_hash": key_hash, "page": 1, "page_size": args.limit},
            timeout=20.0,
        )
        r.raise_for_status()
    except Exception as exc:
        _print_error("recent failures failed", exc, args)
        return 1

    payload = r.json()
    if args.json:
        return _emit_json(payload)

    items: list[dict[str, Any]] = payload.get("items", [])
    console = Console()
    table = Table(title=f"Failures (total={payload.get('total', 0)}, showing={len(items)})", show_header=True)
    table.add_column("#", style="dim", justify="right")
    table.add_column("ID", style="cyan")
    table.add_column("Category")
    table.add_column("Agent")
    table.add_column("Task", overflow="ellipsis", max_width=48)

    for i, item in enumerate(items, start=1):
        table.add_row(
            str(i),
            str(item.get("id", "")),
            str(item.get("failure_category", "")),
            str(item.get("agent_name", "")),
            str(item.get("task_description", "")),
        )
    console.print(table)
    if not items:
        console.print("[dim]No rows. Seed with:[/dim] [bold]python seed_data/seed.py --force[/bold]")
    return 0


def cmd_wisdom(args: argparse.Namespace) -> int:
    key_hash = api_key_hash(args.api_key)
    try:
        r = httpx.get(
            _api(args.backend_url, "/api/sdk/wisdom"),
            params={"task": args.task, "api_key_hash": key_hash},
            timeout=25.0,
        )
        r.raise_for_status()
    except Exception as exc:
        _print_error("wisdom query failed", exc, args)
        return 1

    payload = r.json()
    if args.json:
        return _emit_json(payload)

    wisdom = payload.get("wisdom") or {}
    conf = wisdom.get("confidence_score")
    sim = wisdom.get("similar_failures") or []
    rec = wisdom.get("synthesized_recommendation") or ""
    prefix = payload.get("prompt_prefix") or ""

    console = Console()
    console.print(Panel(rec or "(no recommendation)", title="Synthesized recommendation", border_style="green"))
    if isinstance(conf, (int, float)):
        conf_s = f"{float(conf):.0%}"
    else:
        conf_s = str(conf)
    console.print(f"[bold]Confidence:[/bold] {conf_s}  ·  [bold]Similar matches:[/bold] {len(sim)}")
    if prefix:
        console.print(Panel(prefix, title="Prompt prefix", border_style="yellow"))
    if not sim and conf == 0.0:
        console.print(
            "[dim]Tip:[/dim] Run [bold]python seed_data/seed.py --force[/bold] or fail an instrumented task once "
            "so the graveyard has vectors to match."
        )
    return 0


def _print_error(title: str, exc: BaseException, args: argparse.Namespace) -> None:
    if args.json:
        print(json.dumps({"error": title, "detail": str(exc)}))
        return
    console = Console(stderr=True)
    console.print(f"[red bold]{title}:[/red bold] {exc}")
    console.print(
        "[dim]Tip:[/dim] Use [bold]graveyard --backend-url URL doctor[/bold] or "
        "[bold]graveyard doctor --backend-url URL[/bold]"
    )


EPILOG = """
Examples (--backend-url / --json work before OR after the subcommand):
  graveyard --backend-url http://localhost:8000 doctor
  graveyard doctor --backend-url http://localhost:8000
  graveyard recent --api-key community --backend-url http://localhost:8000
  graveyard --backend-url http://localhost:8000 wisdom --api-key community --task "scrape prices"

  graveyard --json health
"""


def _shared_cli_parser() -> argparse.ArgumentParser:
    """Options repeated on the root parser and each subcommand so both orderings work."""
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        metavar="URL",
        help="Backend API base URL (default: %(default)s)",
    )
    p.add_argument("--json", action="store_true", help="Print raw JSON only (for scripts)")
    return p


def build_parser() -> argparse.ArgumentParser:
    shared = _shared_cli_parser()
    parser = argparse.ArgumentParser(
        prog="graveyard",
        description="Terminal CLI for Agent Graveyard (SDK mode).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
        parents=[shared],
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser(
        "health",
        parents=[shared],
        help="Check backend health (database + Pinecone)",
    )
    h.set_defaults(func=cmd_health)

    d = sub.add_parser(
        "doctor",
        parents=[shared],
        help="Health check plus setup hints when something is wrong",
    )
    d.set_defaults(func=cmd_doctor)

    o = sub.add_parser("overview", parents=[shared], help="Analytics overview for an API key")
    o.add_argument("--api-key", required=True, metavar="KEY", help="raw API key (e.g. community for seeded data)")
    o.set_defaults(func=cmd_overview)

    r = sub.add_parser("recent", parents=[shared], help="List recent stored failures")
    r.add_argument("--api-key", required=True, metavar="KEY", help="raw API key")
    r.add_argument("--limit", type=int, default=10, help="Max rows (backend max 100, default: %(default)s)")
    r.set_defaults(func=cmd_recent)

    w = sub.add_parser("wisdom", parents=[shared], help="Semantic wisdom lookup for a task string")
    w.add_argument("--api-key", required=True, metavar="KEY", help="raw API key")
    w.add_argument("--task", required=True, help="Task description to evaluate")
    w.set_defaults(func=cmd_wisdom)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
