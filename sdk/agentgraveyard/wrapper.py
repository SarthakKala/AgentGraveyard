import asyncio
import functools
import time
import uuid
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
    ):
        self.api_key = api_key
        self.backend_url = backend_url
        self.share_with_community = share_with_community
        self.verbose = verbose
        self.client = GraveyardClient(api_key, backend_url)
        self.logger = GraveyardLogger(verbose=verbose)

    def watch(self, func: Callable):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            session_id = str(uuid.uuid4())
            task_description = kwargs.get("task") or (args[0] if args else func.__name__)
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
            task_description = kwargs.get("task") or (args[0] if args else func.__name__)
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
