import inspect
import types
from collections.abc import Callable
from functools import partial
from typing import Awaitable, NoReturn, TypeVar, cast

from lazy_object_proxy import Proxy
from typing_extensions import ParamSpec


__all__ = ["noop", "raiser", "async_def", "lazy_call", "nulldecorator"]


P = ParamSpec("P")
R = TypeVar("R")


def noop(*_, **__) -> None:
    """A no-op function"""


def raiser(etype: type[BaseException]) -> Callable[..., NoReturn]:
    """
    Create a function that raises the specific exception regardless of the arguments.
    """

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


# Although the return value is actually a Proxy instance, we type annotate it as R,
# because we consider the main goal of type annotations as pragmatism and usefulness to
# programmers. We consider type annotations to be a form of formal API documents, and
# hence should convey the shape of the API as a black box viewed from outside, instead
# of reflecting the API viewed from inside. We are good with and would like to trade
# completeness for pragmatism.
def lazy_call(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    """
    Call a function lazily.

    The return value is lazily evaluated. The actual function execution is delayed until
    the return value is acutally used by external code.
    """

    return cast(R, Proxy(partial(func, args, kwargs)))


def nulldecorator(func: Callable[P, R]) -> Callable[P, R]:
    """A null decorator, intended to be used as a stand-in for an optional decorator"""

    return func
