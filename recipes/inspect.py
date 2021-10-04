import inspect
from collections.abc import Callable
from types import FrameType, FunctionType, LambdaType, MethodType
from typing import Any, Optional

import libcst as cst
import libcst.matchers
from libcst.metadata import PositionProvider
from more_itertools import one
from typing_extensions import ParamSpec

from .builtins import ensure_type, read_text


__all__ = [
    "getsourcefilesource",
    "get_function_body_source",
    "bind_arguments",
    "get_frame_curr_line",
]


P = ParamSpec("P")


def getsourcefilesource(obj: object) -> Optional[str]:
    """
    Return source code of the Python source file where the object is defined, or None if
    not found. Raise TypeError if the object is a built-in module, class or function.
    """

    sourcefile = inspect.getsourcefile(obj)
    return read_text(sourcefile) if sourcefile else None


# TODO in an ideal world, we should annotate the parameter as of type `Union[FunctionType, LambdaType, MethodType]`
# FIXME should not tamper with the outdented comments in the functin body source code.
def get_function_body_source(func: Callable) -> Optional[str]:
    """
    Return source code of the body of the function, or None if not found.
    Raise TypeError if the function is built-in.
    """

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
    pattern = (m.FunctionDef | m.Lambda)(metadata=match_start_line)
    matches = m.findall(wrapper, pattern)

    funcdef = ensure_type(one(matches), (cst.FunctionDef, cst.Lambda))
    body_source = module.code_for_node(funcdef.body)

    return body_source


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
