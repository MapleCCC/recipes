import sys
from collections.abc import Callable, Generator, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from types import TracebackType
from typing import TypeVar

import libcst as cst
import libcst.matchers
from libcst.metadata import PositionProvider
from more_itertools import one
from typing_extensions import ParamSpec

from .builtins import ensure_type
from .functools import noop, raiser
from .inspect import getcallerframe, getsourcefilesource
from .sourcelib import OutdentedCommentError, unindent_source
from .string import remove_leading_newline


__all__ = ["mock_globals", "contextmanagerclass", "skip_context", "literal_block"]


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
    """A helper exception for skipping context"""


@contextmanagerclass
def skip_context() -> Generator[None, None, None]:
    """Return a context manager that skip the body of the with statement."""

    sys.settrace(noop)
    # FIXME magic number is bad
    sys._getframe(2).f_trace = raiser(SkipContext)

    try:
        yield
    except SkipContext:
        pass


class literal_block(AbstractContextManager[str]):
    """
    Transform a block of code to literal string, and not execute the code. This utility
    is useful for writing source code in literal string, and get syntax highlighting
    when viewed in editor.

    Usage:
    ```
    with literal_block() as source:
        a = 1
        b = 2

    print(source)  # "a = 1\\nb = 2"
    ```
    """

    def __enter__(self) -> str:

        frame = getcallerframe()

        source = getsourcefilesource(frame)
        assert source

        module = cst.parse_module(source)
        wrapper = cst.MetadataWrapper(module, unsafe_skip_copy=True)

        m = libcst.matchers
        match_start_line = m.MatchMetadataIfTrue(
            PositionProvider, lambda position: position.start.line == frame.f_lineno
        )
        pattern = m.With(metadata=match_start_line)
        matches = m.findall(wrapper, pattern)

        with_stmt = ensure_type(one(matches), cst.With)
        block_source = module.code_for_node(with_stmt.body)

        # Remove the newline after the colon
        block_source = remove_leading_newline(block_source)

        # Setup skip-context hack
        sys.settrace(noop)
        sys._getframe(1).f_trace = raiser(SkipContext)

        try:
            return unindent_source(block_source)

        except OutdentedCommentError:
            raise ValueError(
                "the block in the body of literal_block() should not contain outdented comments"
            ) from None

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> bool:

        # Suppress the SkipContext exception
        return isinstance(exc_value, SkipContext)
