from collections.abc import Callable
from typing import Protocol, TypeVar

from typing_extensions import ParamSpec


__all__ = [
    "IdentityDecorator",
    "Eq",
    "Ord",
    "SinglePosArgCallable",
    "MultiplePosArgCallable",
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


# TODO can we use @overload to unify OnePargCallable and OnePargUnzeroKargCallable into
# one class instead of two ?


class OnePargCallable(Protocol[T_contra, R_co]):
    def __call__(self, __arg: T_contra) -> R_co:
        ...


class OnePargNonzeroKargCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, __arg: T_contra, **__kwargs: S_contra) -> R_co:
        ...


SinglePosArgCallable = OnePargNonzeroKargCallable[T, S, R] | OnePargCallable[T, R]


class MultiplePosArgCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, *__args: T_contra, **__kwargs: S_contra) -> R_co:
        ...
