import inspect
from collections.abc import Callable
from types import FrameType, FunctionType
from typing import Any, Optional, Union

import libcst as cst
from libcst.helpers import ensure_type
from more_itertools import one
from typing_extensions import ParamSpec

from .sourcelib import unindent_source


__all__ = ["get_function_body_source", "bind_arguments", "get_frame_curr_line"]


P = ParamSpec("P")


def getsourcefilesource(obj: object) -> Optional[str]:
    """
    Return source of the source file where the object is defined, or None if not found.
    Raise TypeError if the object is a built-in module, class or function.
    """

    sourcefile = inspect.getsourcefile(obj)
    return read_text(sourcefile) if sourcefile else None


def get_function_body_source(func: Union[str, FunctionType], unindent: bool = False) -> str:
    """
    Retrieve source code of the body of the function.

    The function is supplied as either a function object (FunctionType), or a string of
    source code.

    Set the `unindent` parameter to `True` to return an unindented source code.
    """

    source = func if isinstance(func, str) else inspect.getsource(func)
    source = unindent_source(source)

    module = cst.parse_module(source)
    funcdef = ensure_type(one(module.body), cst.FunctionDef)
    body_source = module.code_for_node(funcdef.body)

    return unindent_source(body_source) if unindent else body_source


# TODO Any vs object
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

    try:
        return inspect.getsource(frame).splitlines()[frame.f_lineno - 1]
    except OSError:
        return None
