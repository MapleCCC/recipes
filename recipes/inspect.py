import inspect
import sys
from collections.abc import Callable
from types import FrameType, FunctionType, LambdaType, MethodType
from typing import Any, Optional

import libcst as cst
import libcst.matchers
from libcst.metadata import PositionProvider
from more_itertools import one
from typing_extensions import ParamSpec

from .builtins import ensure_type, read_text
from .cst import contains_outdented_comment
from .exceptions import OutdentedCommentError
from .sourcelib import unindent_source
from .string import remove_leading_newline


__all__ = [
    "getsourcefilesource",
    "get_function_body_source",
    "bind_arguments",
    "get_frame_curr_line",
    "getcallerframe",
]


P = ParamSpec("P")


def getsourcefilesource(obj: object) -> Optional[str]:
    """
    Return source code of the Python source file where the object is defined, or None if
    not found. Raise TypeError if the object is a built-in module, class or function.
    """

    sourcefile = inspect.getsourcefile(obj)
    return read_text(sourcefile) if sourcefile else None


# TODO in an ideal world, we should annotate the parameter `func` as of type `Union[FunctionType, LambdaType, MethodType]`
def get_function_body_source(
    func: Callable, *, transform_body: cst.CSTTransformer = None
) -> Optional[str]:
    """
    Return source code of the body of the function, or None if not found.

    Raise `ValueError` if the argument is not a user-defined function. Raise
    `OutdentedCommentError` if the function body contains outdented comments.

    For advanced usage, a custom hook `transform_body` is provided to customize
    and transform the concrete syntax tree node of the function body, before it's
    serialized to a source string.
    """

    # Equivalent to `inspect.isfunction(func) or inspect.ismethod(func)`
    if not isinstance(func, (FunctionType, LambdaType, MethodType)):
        raise ValueError(f"expect a user-defined function, got {func}")

    source = getsourcefilesource(func)
    if source is None:
        return None

    module = cst.parse_module(source)
    wrapper = cst.MetadataWrapper(module, unsafe_skip_copy=True)

    m = libcst.matchers
    match_start_line = m.MatchMetadataIfTrue(
        PositionProvider,
        lambda position: position.start.line == func.__code__.co_firstlineno,
    )
    undeco_func_pattern = (m.FunctionDef | m.Lambda)(metadata=match_start_line)
    deco_func_pattern = m.FunctionDef(
        decorators=[m.Decorator(match_start_line), m.ZeroOrMore(m.Decorator())]
    )
    pattern = undeco_func_pattern | deco_func_pattern

    matches = m.findall(wrapper, pattern)
    funcdef = ensure_type(one(matches), (cst.FunctionDef, cst.Lambda))
    funcbody = funcdef.body

    # Apply the `transform_body` hook
    if transform_body:
        funcbody = ensure_type(funcbody.visit(transform_body), cst.CSTNode)

    # Detect outdented comments before calling libcst.Module.code/code_for_node() whose
    # result is buggy when outdented comments are present.
    if contains_outdented_comment(funcbody):
        raise OutdentedCommentError(
            "get_function_body_source() expects no outdented comments in the body of the function"
        )

    body_source = module.code_for_node(funcbody)

    # Remove the newline following the colon
    body_source = remove_leading_newline(body_source)

    return unindent_source(body_source)


# TODO Any vs object
# TODO can we make the return type something like dict[str, Union[P.args, P.kwargs]] ?
def bind_arguments(
    func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
) -> dict[str, Any]:

    """Bind arguments to function parameters, return the bound arguments as a dict"""

    signature = inspect.signature(func)
    bound_arguments = signature.bind(*args, **kwargs)
    bound_arguments.apply_defaults()

    return bound_arguments.arguments


def get_frame_curr_line(frame: FrameType) -> Optional[str]:
    """Get the current executing source line of a given frame, or None if not found"""

    frame_info = inspect.getframeinfo(frame, context=1)
    context = frame_info.code_context
    if context is None:
        return None
    else:
        return one(context)


def getcallerframe() -> FrameType:
    """Get the frame of the caller."""

    try:
        return sys._getframe(2)

    except ValueError:
        raise RuntimeError(
            "getcallerframe() should be called from inside callable"
        ) from None
