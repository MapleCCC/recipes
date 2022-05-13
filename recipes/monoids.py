import operator
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from functools import partial, reduce
from typing import Generic, TypeVar

import attrs


__all__ = ["Monoid", "BoolAnd", "BoolOr"]


T = TypeVar("T")


# TODO should the type variable T in Monoid[T] be invariant/covariant/contravariant ?

# @attrs.frozen
@dataclass
class Monoid(Generic[T]):
    mempty: T
    mappend: Callable[[T, T], T]
    # mconcat: Callable[[Iterable[T]], T] = partial(reduce, mappend, initializer=mempty)

    def mconcat(self, xs: Iterable[T]) -> T:
        return reduce(self.mappend, xs, self.mempty)


# TODO move to libbool
BoolAnd = Monoid(True, operator.and_)
BoolOr = Monoid(False, operator.or_)
