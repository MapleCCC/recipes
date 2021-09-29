import sys
from collections.abc import MutableSequence
from typing import TypeVar


__all__ = ["hashable", "append", "eval_in_caller_frame"]


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
