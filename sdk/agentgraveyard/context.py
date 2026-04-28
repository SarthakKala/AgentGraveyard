from contextvars import ContextVar

_current_wisdom: ContextVar[str | None] = ContextVar("current_wisdom", default=None)


def set_wisdom(wisdom_text: str) -> None:
    _current_wisdom.set(wisdom_text)


def get_wisdom() -> str | None:
    return _current_wisdom.get()


def clear_wisdom() -> None:
    _current_wisdom.set(None)


def get_wisdom_prompt_prefix() -> str:
    wisdom = get_wisdom()
    return f"{wisdom}\n\n" if wisdom else ""
