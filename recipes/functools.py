import inspect
import types
from collections.abc import Callable
from typing import Awaitable, NoReturn, TypeVar

from typing_extensions import ParamSpec


__all__ = ["noop", "raiser", "async_def"]


P = ParamSpec("P")
R = TypeVar("R")


def noop(*_, **__) -> None:
    """An no-op function"""


def raiser(etype: type[BaseException]) -> Callable[..., NoReturn]:
    """Create a function that raise specific exception regardless of the arguments"""

    def func(*_, **__):
        raise etype

    return func


def async_def(func: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    """Adapt the function such that it behaves as if it was defined with `async def`."""

    code = func.__code__
    new_code = code.replace(co_flags=code.co_flags | inspect.CO_COROUTINE)
    return types.FunctionType(
        new_code, func.__globals__, func.__name__, func.__defaults__, func.__closure__
    )
