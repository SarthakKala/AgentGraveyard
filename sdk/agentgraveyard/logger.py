from rich.console import Console
from rich.panel import Panel


class GraveyardLogger:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.console = Console()

    def _log(self, text: str, style: str) -> None:
        if self.verbose:
            self.console.print(f"[AgentGraveyard] {text}", style=style)

    def banner(self, title: str, body: str, style: str = "cyan") -> None:
        if self.verbose:
            self.console.print(Panel(body, title=title, border_style=style))

    def log_wisdom_scan(self):
        self._log("Pre-task wisdom scan...", "bright_cyan")

    def log_wisdom_found(self, count: int, confidence: float):
        self._log(f"{count} similar failures found", "bright_yellow")
        self._log(
            f"Wisdom briefing ready (confidence: {confidence:.0%}) — prepend get_wisdom_prompt_prefix() to your model input.",
            "bright_green",
        )

    def log_no_warnings(self):
        self._log("No warnings found.", "grey62")

    def log_agent_success(self, execution_time_ms: int):
        self._log(f"Agent succeeded in {execution_time_ms}ms", "bright_green")

    def log_agent_failure(self, error_type: str, error_message: str):
        self._log(f"Agent FAILED: {error_type} - {error_message}", "bright_red")

    def log_coroner_started(self):
        self._log("Coroner Agent diagnosing...", "bright_magenta")

    def log_coroner_complete(self, lesson: str):
        self._log(f"Autopsy complete: {lesson}", "bright_magenta")

    def log_self_heal_started(self):
        self._log("Recording synthesized remediation (backend self-heal step)...", "bright_cyan")

    def log_self_heal_success(self):
        self._log(
            "Remediation text recorded (does not re-run your agent or tools)",
            "bold bright_green",
        )

    def log_self_heal_failed(self):
        self._log("No remediation text recorded for self-heal step.", "bold bright_red")

    def log_failure_id(self, failure_id: str, backend_url: str = "") -> None:
        hint = f" — query: graveyard recent ... (backend {backend_url})" if backend_url else ""
        self._log(f"Recorded failure id={failure_id}{hint}", "bright_blue")
