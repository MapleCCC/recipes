from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec


__all__ = ["IdentityDecorator"]


P = ParamSpec("P")
R = TypeVar("R")


# TODO should it be a Protocol?
class IdentityDecorator:
    def __call__(self, __func: Callable[P, R]) -> Callable[P, R]:
        ...
