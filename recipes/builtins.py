from __future__ import annotations  # for types imported from _typeshed

import sys
from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast, overload

import inflect


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
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


p = inflect.engine()


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

    This is mostly a convenient wrapper to reduce the boilerplate of `open()` and
    `Path.read_text()`. The caller doesn't need to specify the `"r"` and `"t"` flags and
    doesn't need to explicitly specify `encoding="utf-8"` in platforms where
    `locale.getpreferredencoding()` doesn't return "UTF-8".
    """

    with open(file, "r", encoding=encoding) as f:
        return f.read()


def write_text(file: StrPath, text: str, encoding: str = "utf-8") -> None:
    """
    Write text in UTF-8 encoding.

    This is mostly a convenient wrapper to reduce the boilerplate of `open()` and
    `Path.write_text()`. The caller doesn't need to specify the `"w"` and `"t"` flags
    and doesn't need to explicitly specify `encoding="utf-8"` in platforms where
    `locale.getpreferredencoding()` doesn't return "UTF-8".
    """

    with open(file, "w", encoding=encoding) as f:
        f.write(text)


@overload
def ensure_type(obj: object, typ: type[T]) -> T:
    ...


@overload
def ensure_type(obj: object, typ: tuple[type[T]]) -> T:
    ...


@overload
def ensure_type(obj: object, typ: tuple[type[T], type[T2]]) -> Union[T, T2]:
    ...


@overload
def ensure_type(
    obj: object, typ: tuple[type[T], type[T2], type[T3]]
) -> Union[T, T2, T3]:
    ...


@overload
def ensure_type(
    obj: object, typ: tuple[type[T], type[T2], type[T3], type[T4]]
) -> Union[T, T2, T3, T4]:
    ...


@overload
def ensure_type(obj: object, typ: tuple[type[T], ...]) -> T:
    ...


def ensure_type(obj: object, typ: Union[type[T], tuple[type[T], ...]]) -> T:
    """
    Return the same object unchanged, but raise TypeError if the object is not of the
    specified type.

    The `typ` parameter accepts either a type or a tuple of types.
    """

    if isinstance(obj, typ):
        return cast(T, obj)

    else:
        types = typ if isinstance(typ, tuple) else (typ,)
        type_names = [t.__name__ for t in types]
        expected = p.a(p.join(type_names, conj="or"))

        got = p.a(type(obj).__name__)

        raise TypeError(f"expect {expected}, but got {got} instead")
