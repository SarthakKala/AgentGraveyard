import asyncio
import functools
import time
import uuid
import warnings
from typing import Any, Callable

from .client import GraveyardClient
from .context import clear_wisdom, get_wisdom, set_wisdom
from .logger import GraveyardLogger


class GraveyardWrapper:
    def __init__(
        self,
        api_key: str,
        backend_url: str = "https://api.agentgraveyard.dev",
        share_with_community: bool = False,
        verbose: bool = True,
        task_param: str | None = None,
    ):
        """
        task_param: Name of the keyword argument that carries the human-readable task string for
        wisdom retrieval (e.g. "task" or "task_description"). If None, tries "task_description",
        then "task", then the first positional argument (warning if multiple positional args).
        """
        self.api_key = api_key
        self.backend_url = backend_url
        self.share_with_community = share_with_community
        self.verbose = verbose
        self.task_param = task_param
        self.client = GraveyardClient(api_key, backend_url)
        self.logger = GraveyardLogger(verbose=verbose)

    def _resolve_task_description(self, func: Callable, args: tuple, kwargs: dict) -> str:
        if self.task_param:
            if self.task_param in kwargs:
                return str(kwargs[self.task_param])
            warnings.warn(
                f"GraveyardWrapper(task_param={self.task_param!r}) but call did not pass "
                f"keyword {self.task_param!r}; falling back to legacy rules.",
                UserWarning,
                stacklevel=3,
            )
        for key in ("task_description", "task"):
            if key in kwargs:
                return str(kwargs[key])
        if args:
            if len(args) > 1:
                warnings.warn(
                    "Multiple positional arguments without task_description=/task= — using "
                    "args[0] for the wisdom query; pass an explicit task string to avoid wrong matches.",
                    UserWarning,
                    stacklevel=3,
                )
            return str(args[0])
        return func.__name__

    def watch(self, func: Callable):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            session_id = str(uuid.uuid4())
            task_description = self._resolve_task_description(func, args, kwargs)
            self.logger.log_wisdom_scan()
            wisdom = asyncio.run(self.client.query_wisdom(str(task_description)))
            wisdom_payload = wisdom.get("wisdom", {})
            if wisdom_payload.get("has_warnings"):
                set_wisdom(wisdom.get("prompt_prefix", ""))
                self.logger.log_wisdom_found(
                    len(wisdom_payload.get("similar_failures", [])),
                    float(wisdom_payload.get("confidence_score", 0.0)),
                )
            else:
                clear_wisdom()
                self.logger.log_no_warnings()
            asyncio.run(
                self.client.send_event(
                    "TASK_START",
                    func.__name__,
                    str(task_description),
                    {"session_id": session_id},
                )
            )
            started = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed = int((time.perf_counter() - started) * 1000)
                asyncio.run(
                    self.client.send_event(
                        "TASK_SUCCESS",
                        func.__name__,
                        str(task_description),
                        {"session_id": session_id, "execution_time_ms": elapsed},
                    )
                )
                self.logger.log_agent_success(elapsed)
                return result
            except Exception as exc:
                self.logger.log_agent_failure(type(exc).__name__, str(exc))
                self.logger.log_coroner_started()
                asyncio.run(
                    self.client.send_event(
                        "TASK_FAILURE",
                        func.__name__,
                        str(task_description),
                        {
                            "session_id": session_id,
                            "error_type": type(exc).__name__,
                            "error_message": str(exc),
                            "tools_attempted": [],
                            "share_with_community": self.share_with_community,
                        },
                    )
                )
                raise
            finally:
                clear_wisdom()

        return wrapped

    def watch_async(self, func: Callable):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            session_id = str(uuid.uuid4())
            task_description = self._resolve_task_description(func, args, kwargs)
            self.logger.log_wisdom_scan()
            wisdom = await self.client.query_wisdom(str(task_description))
            wisdom_payload = wisdom.get("wisdom", {})
            if wisdom_payload.get("has_warnings"):
                set_wisdom(wisdom.get("prompt_prefix", ""))
                self.logger.log_wisdom_found(
                    len(wisdom_payload.get("similar_failures", [])),
                    float(wisdom_payload.get("confidence_score", 0.0)),
                )
            else:
                clear_wisdom()
                self.logger.log_no_warnings()
            await self.client.send_event("TASK_START", func.__name__, str(task_description), {"session_id": session_id})
            started = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                elapsed = int((time.perf_counter() - started) * 1000)
                await self.client.send_event(
                    "TASK_SUCCESS",
                    func.__name__,
                    str(task_description),
                    {"session_id": session_id, "execution_time_ms": elapsed},
                )
                self.logger.log_agent_success(elapsed)
                return result
            except Exception as exc:
                self.logger.log_agent_failure(type(exc).__name__, str(exc))
                self.logger.log_coroner_started()
                await self.client.send_event(
                    "TASK_FAILURE",
                    func.__name__,
                    str(task_description),
                    {
                        "session_id": session_id,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc),
                        "tools_attempted": [],
                        "share_with_community": self.share_with_community,
                    },
                )
                raise
            finally:
                clear_wisdom()

        return wrapped

    async def query_wisdom(self, task_description: str) -> dict[str, Any]:
        return await self.client.query_wisdom(task_description)

    def get_current_wisdom(self) -> str | None:
        return get_wisdom()
