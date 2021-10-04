from __future__ import annotations  # for types imported from _typeshed

import sys
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any, TypeVar


if TYPE_CHECKING:
    from _typeshed import StrPath


__all__ = [
    "hashable",
    "append",
    "eval_in_caller_frame",
    "NO_ARGUMENT",
    "read_text",
    "write_text",
]


T = TypeVar("T")


def hashable(obj: object, /) -> bool:
    """Check if an object is hashable"""

    try:
        hash(obj)
    except TypeError:
        return False
    else:
        return True


def append(seq: MutableSequence[T], elem: T) -> int:
    """Append an element to a sequence, and return the new length of the sequence."""

    seq.append(elem)
    return len(seq) - 1


def eval_in_caller_frame(expr: str):
    """Evaluate the expression in caller's frame"""

    frame = sys._getframe(2)
    return eval(expr, frame.f_globals, frame.f_locals)


# A sentinel object to represent no argument to a parameter of a callable.
NO_ARGUMENT: Any = object()


def read_text(file: StrPath, encoding: str = "utf-8") -> str:
    """
    Read text in UTF-8 encoding.

    This is mostly a convenient utility to replace the boilerplate code when using
    `open()` or `Path.read_text()`, since the caller doesn't need to specify the `"r"`
    and `"t"` flags and doesn't need to explicitly specify `encoding="utf-8"` in
    platforms where the `locale.getpreferredencoding()` doesn't return UTF-8.
    """

    with open(file, "r", encoding=encoding) as f:
        return f.read()


def write_text(file: StrPath, text: str, encoding: str = "utf-8") -> None:
    """
    Write text in UTF-8 encoding.

    This is mostly a convenient utility to replace the boilerplate code when using
    `open()` or `Path.write_text()`, since the caller doesn't need to specify the `"w"`
    and `"t"` flags and doesn't need to explicitly specify `encoding="utf-8"` in
    platforms where the `locale.getpreferredencoding()` doesn't return UTF-8.
    """

    with open(file, "w", encoding=encoding) as f:
        f.write(text)
