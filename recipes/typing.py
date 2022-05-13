from collections.abc import Callable
from typing import Protocol, TypeVar

from typing_extensions import ParamSpec


__all__ = [
    "IdentityDecorator",
    "Eq",
    "Ord",
    "SinglePosArgCallable",
    "MultiplePosArgCallable",
    "AnyPosArgCallable",
]


T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
S = TypeVar("S")
S_contra = TypeVar("S_contra", contravariant=True)
R_co = TypeVar("R_co", covariant=True)

P = ParamSpec("P")
R = TypeVar("R")


# TODO should it be a Protocol?
class IdentityDecorator:
    def __call__(self, __func: Callable[P, R]) -> Callable[P, R]:
        ...


class Eq(Protocol):
    def __eq__(self, __other) -> bool:
        return self == __other

    def __ne__(self, __other) -> bool:
        return not self.__eq__(__other)


class Ord(Eq, Protocol):
    def __lt__(self, __other) -> bool:
        return self < __other

    def __le__(self, __other) -> bool:
        return self.__lt__(__other) or self.__eq__(__other)

    def __gt__(self, __other) -> bool:
        return not self.__le__(__other)

    def __ge__(self, __other) -> bool:
        return not self.__lt__(__other)


class P0K0Callable(Protocol[R_co]):
    def __call__(self) -> R_co:
        ...


class P0KPCallable(Protocol[T_contra, R_co]):
    def __call__(self, **__kwarg: T_contra) -> R_co:
        ...


class PPK0Callable(Protocol[T_contra, R_co]):
    def __call__(self, *__args: T_contra) -> R_co:
        ...


class PPKPCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, *__args: T_contra, **__kwargs: S_contra) -> R_co:
        ...


# TODO can we use @overload to unify P1K0Callable and P1KPCallable into
# one class instead of two ?


class P1K0Callable(Protocol[T_contra, R_co]):
    def __call__(self, __arg: T_contra) -> R_co:
        ...


class P1KPCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, __arg: T_contra, **__kwargs: S_contra) -> R_co:
        ...


P1Callable = P1KPCallable[T, S, R] | P1K0Callable[T, R]
PPCallable = PPKPCallable[T, S, R] | PPK0Callable[T, R]
PNCallable = P1Callable[T, S, R] | PPCallable[T, S, R]

SinglePosArgCallable = P1Callable[T, S, R]
MultiplePosArgCallable = PPCallable[T, S, R]
AnyPosArgCallable = PNCallable[T, S, R]
