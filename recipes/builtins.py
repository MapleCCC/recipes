from collections.abc import MutableSequence
from typing import TypeVar


__all__ = ["hashable", "append"]


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
