from rich.console import Console


class GraveyardLogger:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.console = Console()

    def _log(self, text: str, style: str) -> None:
        if self.verbose:
            self.console.print(f"[AgentGraveyard] {text}", style=style)

    def log_wisdom_scan(self):
        self._log("Pre-task wisdom scan...", "cyan")

    def log_wisdom_found(self, count: int, confidence: float):
        self._log(f"{count} similar failures found", "yellow")
        self._log(f"Wisdom injected (confidence: {confidence:.0%})", "green")

    def log_no_warnings(self):
        self._log("No warnings found.", "dim")

    def log_agent_success(self, execution_time_ms: int):
        self._log(f"Agent succeeded in {execution_time_ms}ms", "green")

    def log_agent_failure(self, error_type: str, error_message: str):
        self._log(f"Agent FAILED: {error_type} - {error_message}", "red")

    def log_coroner_started(self):
        self._log("Coroner Agent diagnosing...", "magenta")

    def log_coroner_complete(self, lesson: str):
        self._log(f"Autopsy complete: {lesson}", "magenta")

    def log_self_heal_started(self):
        self._log("Self-heal attempt starting...", "cyan")

    def log_self_heal_success(self):
        self._log("Self-heal SUCCEEDED", "bold green")

    def log_self_heal_failed(self):
        self._log("Self-heal FAILED. New tombstone.", "bold red")

    def log_dashboard_url(self, failure_id: str, base_url: str):
        self._log(f"View full report: {base_url}/failure/{failure_id}", "blue")
