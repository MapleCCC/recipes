from __future__ import annotations  # for types imported from _typeshed

import atexit
import sys
from collections.abc import Callable, Iterable, MutableSequence
from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

import click
import inflect


if TYPE_CHECKING:
    from _typeshed import StrPath


__all__ = [
    "hashable",
    "append",
    "apply",
    "getattr_r",
    "setattr_r",
    "eval_in_caller_frame",
    "NO_ARGUMENT",
    "read_text",
    "write_text",
    "ensure_type",
    "try_decode",
    "schedule_pause_at_exit",
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
    """Append an element to a sequence, and return the insertion index."""

    seq.append(elem)
    return len(seq) - 1


def apply(func: Callable[[T], None], iterable: Iterable[T]) -> None:
    for elem in iterable:
        func(elem)


# The `getattr_r` and `setattr_r` routines are intended as in-place replacements to the
# builtin `getattr` and `setattr` routines. The new APIs are specifically designed to
# make elegant the handling of boundary conditions / edge cases, and hence enhance code
# writability & readability, and reduce code boilerplates.
#
# Possible usage:
# `from recipes.builtins import getattr_r as getattr, setattr_r as setattr`


NO_ATTR = object()  # A sentinel to denote the absence of an attribute


def getattr_r(obj: object, attr: str) -> Any:
    return getattr(obj, attr, NO_ATTR)


def setattr_r(obj: object, attr: str, value: object) -> None:
    if value is NO_ATTR:
        delattr(obj, attr)
    else:
        setattr(obj, attr, value)


# TODO deprecate
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
def ensure_type(obj: object, typ: tuple[type[T], type[T1]]) -> T | T1:
    ...


@overload
def ensure_type(obj: object, typ: tuple[type[T], type[T1], type[T2]]) -> T | T1 | T2:
    ...


@overload
def ensure_type(
    obj: object, typ: tuple[type[T], type[T1], type[T2], type[T3]]
) -> T | T1 | T2 | T3:
    ...


@overload
def ensure_type(obj: object, typ: tuple[type[T], ...]) -> T:
    ...


def ensure_type(obj: object, typ: type[T] | tuple[type[T], ...]) -> T:
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


def try_decode(blob: bytes) -> str:
    """First try to decode with UTF-8, and fallback to use cchardet if fails"""

    try:
        return blob.decode(encoding="utf-8")

    except UnicodeDecodeError:

        import cchardet

        detected_encoding = cchardet.detect(blob)["encoding"]
        return blob.decode(detected_encoding)


registered = False

# Wrap `click.pause()` into a private function, because `atexit.unregister()` will
# unregister every occurrence of the function in the atexit call stack. It's possible
# that other code registers `click.pause()` and we don't want to accidentally remove
# theirs.
my_pause = lambda msg: click.pause(msg)


def schedule_pause_at_exit(message: str | None = None) -> None:

    global registered

    if registered:
        raise RuntimeError("pause-at-exit has already been scheduled")

    if message is None:
        message = "Press any key to exit"

    atexit.register(my_pause, message)

    registered = True


def cancel() -> None:
    global registered
    atexit.unregister(my_pause)
    registered = False


schedule_pause_at_exit.cancel = cancel


def lines(s: str) -> list[str]:
    return s.splitlines()


def unlines(l: list[str]) -> str:
    return "\n".join(l)
