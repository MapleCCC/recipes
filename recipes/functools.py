import inspect
import types
from collections.abc import Callable
from functools import partial, wraps
from typing import Any, Awaitable, Concatenate, NoReturn, ParamSpec, TypeVar, cast

from lazy_object_proxy import Proxy

from .monoids import Monoid
from .typing import MultiplePosArgCallable, SinglePosArgCallable


__all__ = [
    "noop",
    "raiser",
    "async_def",
    "lazy_call",
    "nulldecorator",
    "inject_pre_hook",
    "inject_post_hook",
    "mapreduce",
]


T = TypeVar("T")
S = TypeVar("S")

P = ParamSpec("P")
R = TypeVar("R")
R2 = TypeVar("R2")


def noop(*_: Any, **__: Any) -> None:
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
    new_func = types.FunctionType(
        new_code, func.__globals__, func.__name__, func.__defaults__, func.__closure__
    )

    return cast(Callable[P, Awaitable[R]], new_func)


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
    the return value is acutally used by the external code.
    """

    return cast(R, Proxy(partial(func, *args, **kwargs)))


# TODO update the type annotation to reflect the fact that nulldecorator can also be
# applied onto a class definition.

# TODO can be further simplied to be sth like:
# ```
# nulldecorator: IdentityDecorator = identity
# ```

def nulldecorator(func: Callable[P, R]) -> Callable[P, R]:
    """A null decorator, intended to be used as a stand-in for an optional decorator"""

    return func


def inject_pre_hook(prehook: Callable[P, None], func: Callable[P, R]) -> Callable[P, R]:
    """Inject pre hook into a function"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        prehook(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def inject_post_hook(
    posthook: Callable[Concatenate[R, P], R2], func: Callable[P, R]
) -> Callable[P, R2]:
    """Inject post hook into a function"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R2:
        result = func(*args, **kwargs)
        return posthook(result, *args, **kwargs)

    return wrapper


# TODO what's the conventional name of such a function (Monoid a)->(b->a)->(list b)->a ?
# TODO use curry tricks to flatten code indentation level

def mapreduce(
    monoid: Monoid[R],
) -> Callable[[SinglePosArgCallable[T, S, R]], MultiplePosArgCallable[T, S, R]]:
    """Transform a function that returns monoid such that it can receive an iterable of input"""

    def decorator(
        func: SinglePosArgCallable[T, S, R]
    ) -> MultiplePosArgCallable[T, S, R]:

        @wraps(func)
        def wrapper(*xs: T, **kwargs: S) -> R:
            return monoid.mconcat(func(x, **kwargs) for x in xs)

        return wrapper

    return decorator
