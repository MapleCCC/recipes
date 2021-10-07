import inspect
import sys
from collections.abc import Callable, Generator, Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from inspect import Parameter
from types import FunctionType, TracebackType
from typing import Any, TypeVar, Union, overload

import libcst as cst
import libcst.matchers
from libcst.metadata import PositionProvider
from more_itertools import one
from typing_extensions import ParamSpec

from .builtins import ensure_type
from .cst import contains_outdented_comment
from .exceptions import OutdentedCommentError
from .functools import noop, raiser
from .inspect import get_function_body_source, getcallerframe, getsourcefilesource
from .sourcelib import unindent_source


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


class literal_block_context(AbstractContextManager[str]):
    """
    Return a context manager that returns the source code of the block in its body from
    `__enter__`, and not execute the code.
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
        with_stmt_body = with_stmt.body

        # Detect outdented comments before calling libcst.Module.code/code_for_node()
        # whose result is buggy when outdented comments are present.
        if contains_outdented_comment(with_stmt_body):
            raise OutdentedCommentError(
                "the block in the body of literal_block() should not contain outdented comments"
            )

        block_source = module.code_for_node(with_stmt_body)

        if isinstance(with_stmt_body, cst.IndentedBlock):
            # Remove the header following the colon
            block_source = "".join(block_source.splitlines(keepends=True)[1:])

        # Setup skip-context hack
        sys.settrace(noop)
        sys._getframe(1).f_trace = raiser(SkipContext)

        return unindent_source(block_source)

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> bool:

        # Suppress the SkipContext exception
        return isinstance(exc_value, SkipContext)


@overload
def literal_block() -> AbstractContextManager[str]:
    ...


@overload
def literal_block(func: Callable) -> str:
    ...


def literal_block(func: Callable = None) -> Union[str, AbstractContextManager[str]]:
    """
    Transform a block of code to literal string, and not execute the code. This utility
    is useful for writing source code in the form of literal string, while getting
    syntax highlighting viewed in editor.

    Raise `ValueError` if the decorated function is not a user-defined function. Raise
    `OutdentedCommentError` if the body of the decorated function contains outdented
    comments. Raise `NameError` if a replacement field finds no replacement.

    Usage:

    1. Used as a context manager:

        ```
        with literal_block() as source:
            a = 1
            b = 2

        print(source)  # "a = 1\\nb = 2"
        ```

    2. Used as a decorator:

        ```
        @literal_block
        def source():
            a = 1
            b = 2

        print(source)  # "a = 1\\nb = 2"
        ```

        The decorated function's parameters are treated as replacement field names,
        whose occurrences in the body of the decorated function are replaced by the
        formatted values of variables with the same names, looked up in the environment
        where the decoration happens. The behavior is similar to that of [formatted string literals](https://docs.python.org/3.9/reference/lexical_analysis.html#f-strings).

        ```
        c = 3

        @literal_block
        def source(c):
            a = 1
            b = c

        print(source)  # 'a = 1\\nb = "3"'
        ```

        The parameter's default value is treated as fall-back value for the replacement
        field when the name lookup fails in the environment where the decoration
        happens.

        ```
        @literal_block
        def source(d = 4):
            a = 1
            b = d

        print(source)  # 'a = 1\\nb = "4"'
        ```
    """

    # TODO maybe we can merge parts of the impl of decorator and context

    if not func:
        return literal_block_context()

    if not isinstance(func, FunctionType):
        raise ValueError(f"expect a user-defined function, got {func}")

    signature = inspect.signature(func)

    if not all(
        param.kind is Parameter.POSITIONAL_OR_KEYWORD
        for param in signature.parameters.values()
    ):
        raise ValueError(
            "the function decorated by @literal_block should only have postional-or-keyword parameters"
        )

    m = libcst.matchers

    class SurroundReplacementFieldsWithCurlyBraces(m.MatcherDecoratableTransformer):

        @m.leave(m.Name(m.OneOf(*signature.parameters)))
        def surround_with_curly_braces(
            self, original_node: cst.Name, updated_node: cst.Name
        ) -> cst.Set:
            return cst.Set([cst.Element(updated_node)])

    try:
        transformer = SurroundReplacementFieldsWithCurlyBraces()
        body_source = get_function_body_source(func, transform_body=transformer)

    except OutdentedCommentError:
        raise OutdentedCommentError(
            "@literal_block expects no outdented comments in the body of the decorated function"
        ) from None

    repls: dict[str, Any] = {}
    for name, param in signature.parameters.items():
        try:
            frame = getcallerframe()
            repls[name] = eval(name, frame.f_globals, frame.f_locals)
        except NameError:
            if param.default is Parameter.empty:
                raise NameError(f"{name} has no replacement found") from None
            repls[name] = param.default

    return body_source.format_map(repls)
