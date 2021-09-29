import re
import sys
from collections.abc import Callable, Generator, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from typing import TypeVar

from typing_extensions import ParamSpec

from .functools import noop, raiser
from .inspect import get_frame_curr_line


__all__ = ["mock_globals", "contextmanagerclass", "skip_context"]


P = ParamSpec("P")
R = TypeVar("R")


@contextmanager
def mock_globals(symbol_table: Mapping[str, object]) -> Iterator[None]:
    """Temporarily mock the global symbol table"""

    origin_globals = globals().copy()

    globals_dict = globals()
    globals_dict.clear()
    globals_dict |= symbol_table

    try:
        yield
    finally:
        globals_dict.clear()
        globals_dict |= origin_globals


def contextmanagerclass(
    func: Callable[P, Generator[R, None, None]]
) -> type[AbstractContextManager[R]]:
    """
    Similar to `contextlib.contextmanager`, but create a class that spawns context
    managers, instead of a factory function that spawns context managers, such that
    subclassing, mixin, customization are possible.
    """

    class wrapper:
        def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
            self._args = args
            self._kwargs = kwargs

        def __enter__(self) -> R:
            self._gen = func(*self._args, **self._kwargs)
            return next(self._gen)

        def __exit__(self, exc_type, exc_value, traceback) -> bool:
            if exc_type is None:
                try:
                    next(self._gen)
                except StopIteration:
                    return True
                else:
                    raise RuntimeError("generator didn't stop")

            else:
                try:
                    self._gen.throw(exc_type, exc_value, traceback)
                except exc_type:
                    return False
                except StopIteration:
                    return True
                else:
                    raise RuntimeError("generator didn't stop")

    return wrapper



class SkipContext(Exception):
    """A helper exception for `skip_context()`"""


@contextmanagerclass
def skip_context() -> Generator[None, None, None]:
    """Return a context manager that skip the body of the with statement."""

    sys.settrace(noop)

    frame = sys._getframe(1)
    while (line := get_frame_curr_line(frame)) and re.fullmatch(
        r"\s*with (?P<context_manager>.+):\s*(?P<comment>#.*)?", line
    ):
        frame = frame.f_back
        assert frame is not None
    frame.f_trace = raiser(SkipContext)

    try:
        yield
    except SkipContext:
        pass
