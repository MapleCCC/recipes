from __future__ import annotations

import asyncio
import inspect
import types
from collections.abc import Callable
from functools import partial, wraps
from inspect import Parameter, isasyncgenfunction
from typing import (
    Any,
    Awaitable,
    Concatenate,
    NoReturn,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    overload,
)

from lazy_object_proxy import Proxy
from typing_extensions import Self

from .monoids import Monoid
from .typing import K0Callable, P1Callable, P1K0Callable, PNCallable, PNK0Callable


__all__ = [
    "noop",
    "raiser",
    "async_def",
    "lazy_call",
    "nulldecorator",
    "inject_pre_hook",
    "inject_post_hook",
    "curry",
    "mapreduce",
]


T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
T1 = TypeVar("T1")
T2 = TypeVar("T2")

S = TypeVar("S")

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)
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


def is_positional_parameter(param: Parameter) -> bool:
    return param.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)


def is_mandatory_positional_parameter(param: Parameter) -> bool:
    return is_positional_parameter(param) and param.default is Parameter.empty


class CurriedCallable(Protocol[T_contra, R_co]):
    def __call__(self, *__x: T_contra) -> Self | R_co:
        ...


def curry(func: K0Callable[T, R]) -> CurriedCallable[T, R]:

    params = inspect.signature(func).parameters.values()

    if not all(is_mandatory_positional_parameter(p) for p in params):
        raise ValueError(
            "@curry decorates function with only mandatory positional parameters"
        )

    class intermediate:
        """Intermediate object"""

        def __init__(self, *args: T) -> None:
            self.args = args

        __slots__ = "args"

        def __call__(self, *args: T) -> intermediate | R:

            rem = len(params) - len(self.args) - len(args)

            if rem > 0:
                return intermediate(*self.args, *args)
            elif rem == 0:
                return func(*self.args, *args)
            else:
                raise ValueError("too many arguments")

    return intermediate


def curry1(func: Callable[[T], R]) -> Callable[[T], R]:
    return cast(Callable[[T], R], curry(func))


def curry2(func: Callable[[T, S], R]) -> Callable[[T], Callable[[S], R]]:
    return cast(Callable[[T], Callable[[S], R]], curry(func))


def curry3(
    func: Callable[[T, T1, T2], R]
) -> Callable[[T], Callable[[T1], Callable[[T2], R]]]:
    return cast(Callable[[T], Callable[[T1], Callable[[T2], R]]], curry(func))


# TODO what's the conventional name of such a function (Monoid a)->(b->a)->(list b)->a ?

# TODO Ask pyright developers why applying curry2() to an @overload function leads to
# such problem ?
#
# fmt: off
# @overload
# def _mapreduce(monoid: Monoid[R], func: P1Callable[T, S, Awaitable[R]]) -> PNCallable[T, S, Awaitable[R]]: ...
# @overload
# def _mapreduce(monoid: Monoid[R], func: P1Callable[T, S, R]) -> PNCallable[T, S, R]: ...
# fmt: on


@curry2
def _mapreduce(
    monoid: Monoid[R], func: P1Callable[T, S, R | Awaitable[R]]
) -> PNCallable[T, S, R | Awaitable[R]]:
    """Transform a function that returns monoid such that it can receive an iterable of input"""

    if isasyncgenfunction(func):
        async_func = cast(P1Callable[T, S, Awaitable[R]], func)

        @wraps(func)
        async def async_wrapper(*xs: T, **kwargs: S) -> R:
            coros = (async_func(x, **kwargs) for x in xs)
            rets = await asyncio.gather(*coros)
            return monoid.mconcat(rets)

        return async_wrapper

    else:
        sync_func = cast(P1Callable[T, S, R], func)

        @wraps(func)
        def wrapper(*xs: T, **kwargs: S) -> R:
            return monoid.mconcat(sync_func(x, **kwargs) for x in xs)

        return wrapper


# Use a temporary Protocol to express the return type of `mapreduce()`. Hopefully in the
# future we don't have to do such dirty hacks when Python static type system becomes
# more powerful and expressive.


class mapreduce_return_type(Protocol[R]):
    # Specialized overload for common case
    @overload
    def __call__(
        self, __func: P1K0Callable[T, Awaitable[R]]
    ) -> PNK0Callable[T, Awaitable[R]]:
        ...

    @overload
    def __call__(
        self, __func: P1Callable[T, S, Awaitable[R]]
    ) -> PNCallable[T, S, Awaitable[R]]:
        ...

    # Specialized overload for common case
    @overload
    def __call__(self, __func: P1K0Callable[T, R]) -> PNK0Callable[T, R]:
        ...

    @overload
    def __call__(self, __func: P1Callable[T, S, R]) -> PNCallable[T, S, R]:
        ...


def mapreduce(monoid: Monoid[R]) -> mapreduce_return_type[R]:
    return cast(mapreduce_return_type[R], _mapreduce(monoid))
