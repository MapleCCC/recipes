from collections.abc import Callable
from typing import ParamSpec, Protocol, TypeVar


__all__ = ["IdentityDecorator", "Eq", "Ord"]


T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)
T1_contra = TypeVar("T1_contra", contravariant=True)
T2_contra = TypeVar("T2_contra", contravariant=True)
T3_contra = TypeVar("T3_contra", contravariant=True)
T4_contra = TypeVar("T4_contra", contravariant=True)

S = TypeVar("S")
S_contra = TypeVar("S_contra", contravariant=True)
S1_contra = TypeVar("S1_contra", contravariant=True)
S2_contra = TypeVar("S2_contra", contravariant=True)
S3_contra = TypeVar("S3_contra", contravariant=True)
S4_contra = TypeVar("S4_contra", contravariant=True)

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


# fmt: off
class P0K0Callable(Protocol[R_co]):
    def __call__(self) -> R_co: ...
class P0KNCallable(Protocol[T_contra, R_co]):
    def __call__(self, **__kwarg: T_contra) -> R_co: ...
class PNK0Callable(Protocol[T_contra, R_co]):
    def __call__(self, *__args: T_contra) -> R_co: ...
class PNKNCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, *__args: T_contra, **__kwargs: S_contra) -> R_co: ...
# fmt: on


# TODO can we use @overload to unify these classes into one ?


# fmt: off
class P1K0Callable(Protocol[T_contra, R_co]):
    def __call__(self, __arg: T_contra) -> R_co: ...
class P2K0Callable(Protocol[T_contra, T1_contra, R_co]):
    def __call__(self, __x: T_contra, __x1: T1_contra) -> R_co: ...
class P3K0Callable(Protocol[T_contra, T1_contra, T2_contra, R_co]):
    def __call__(self, __x: T_contra, __x1: T1_contra, __x2: T2_contra) -> R_co: ...
class P4K0Callable(Protocol[T_contra, T1_contra, T2_contra, T3_contra, R_co]):
    def __call__(self, __x: T_contra, __x1: T1_contra, __x2: T2_contra, __x3: T3_contra) -> R_co: ...
class P5K0Callable(Protocol[T_contra, T1_contra, T2_contra, T3_contra, T4_contra, R_co]):
    def __call__(self, __x: T_contra, __x1: T1_contra, __x2: T2_contra, __x3: T3_contra, __x4: T4_contra,) -> R_co: ...
# fmt: on


K0Callable = (
    PNK0Callable[T, R]
    | P5K0Callable[T, T, T, T, T, R]
    | P4K0Callable[T, T, T, T, R]
    | P3K0Callable[T, T, T, R]
    | P2K0Callable[T, T, R]
    | P1K0Callable[T, R]
    | P0K0Callable[R]
)


# fmt: off
class P1K1Callable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, __arg: T_contra, *, __x: S_contra) -> R_co: ...
class P1K2Callable(Protocol[T_contra, S_contra, S1_contra, R_co]):
    def __call__(self, __arg: T_contra, *, __x: S_contra, __x1: S1_contra) -> R_co: ...
class P1K3Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, R_co]):
    def __call__(self, __arg: T_contra, *, __x: S_contra, __x1: S1_contra, __x2: S2_contra) -> R_co: ...
class P1K4Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, S3_contra, R_co]):
    def __call__(self, __arg: T_contra, *, __x: S_contra, __x1: S1_contra, __x2: S2_contra, __x3: S3_contra) -> R_co: ...
class P1K5Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, S3_contra, S4_contra, R_co]):
    def __call__(self, __arg: T_contra, *, __x: S_contra, __x1: S1_contra, __x2: S2_contra, __x3: S3_contra, __x4: S4_contra) -> R_co: ...
class P1KNCallable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, __arg: T_contra, **__kwargs: S_contra) -> R_co: ...
# fmt: on


P1Callable = (
    P1KNCallable[T, S, R]
    | P1K5Callable[T, S, S, S, S, S, R]
    | P1K4Callable[T, S, S, S, S, R]
    | P1K3Callable[T, S, S, S, R]
    | P1K2Callable[T, S, S, R]
    | P1K1Callable[T, S, R]
    | P1K0Callable[T, R]
)


# fmt: off
class PNK1Callable(Protocol[T_contra, S_contra, R_co]):
    def __call__(self, *__args: T_contra, __x: S_contra) -> R_co: ...
class PNK2Callable(Protocol[T_contra, S_contra, S1_contra, R_co]):
    def __call__(self, *__args: T_contra, __x: S_contra, __x1: S1_contra) -> R_co: ...
class PNK3Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, R_co]):
    def __call__(self, *__args: T_contra, __x: S_contra, __x1: S1_contra, __x2: S2_contra) -> R_co: ...
class PNK4Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, S3_contra, R_co]):
    def __call__(self, *__args: T_contra, __x: S_contra, __x1: S1_contra, __x2: S2_contra, __x3: S3_contra) -> R_co: ...
class PNK5Callable(Protocol[T_contra, S_contra, S1_contra, S2_contra, S3_contra, S4_contra, R_co]):
    def __call__(self, *__args: T_contra, __x: S_contra, __x1: S1_contra, __x2: S2_contra, __x3: S3_contra, __x4: S4_contra) -> R_co: ...
# fmt: on


PNCallable = (
    PNKNCallable[T, S, R]
    | PNK5Callable[T, S, S, S, S, S, R]
    | PNK4Callable[T, S, S, S, S, R]
    | PNK3Callable[T, S, S, S, R]
    | PNK2Callable[T, S, S, R]
    | PNK1Callable[T, S, R]
    | PNK0Callable[T, R]
)


# TODO programmatically generate instead of hand-written
#
# PKCallable = (
#     PNCallable[T, S, R]
#     | P5Callable[T, S, R]
#     | P4Callable[T, S, R]
#     | P3Callable[T, S, R]
#     | P2Callable[T, S, R]
#     | P1Callable[T, S, R]
#     | P0Callable[S, R]
# )

# TODO move to `typing.callables` module
# TODO maybe make it a standalone library ?
