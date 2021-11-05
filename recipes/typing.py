from collections.abc import Callable
from typing import Protocol, TypeVar

from typing_extensions import ParamSpec


__all__ = ["IdentityDecorator", "Eq", "Ord"]


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
