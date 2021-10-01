import inspect
import parser
import symbol
from collections.abc import Callable
from types import FrameType, FunctionType
from typing import Any, Optional, Union

from typing_extensions import ParamSpec

from .sourcelib import unindent_source


__all__ = ["get_function_body_source", "bind_arguments", "get_frame_curr_line"]


P = ParamSpec("P")


# FIXME It is quite insane to use a sequence of magic numbers to inspect syntax tree.
#     Let's use an object-oriented concrete syntax tree library instead.


def get_function_body_source(func: Union[str, FunctionType], unindent: bool = False) -> str:
    """
    Retrieve source code of the body of the function.

    The function is supplied as either a function object (FunctionType), or a string of
    source code.

    Set the `unindent` parameter to `True` to return an unindented source code.
    """

    # 1. Retrieve source code of the function, which is then parsed into concrete syntax
    # tree.
    #
    # 2. Inspect the concrete syntax tree, and locate the position of the colon token
    # which marks the delimitation between function header and function body.
    #
    # 3. Extract the source code of function body after the source line of the colon
    # token.

    source = func if isinstance(func, str) else inspect.getsource(func)

    syntax_tree = parser.suite(unindent_source(source))

    # Convert syntax tree to tuple representation
    st_tuple = syntax_tree.totuple(line_info=True)

    # Locate the colon token that marks the delimitations between function header and
    # function body.
    #
    # Node chain: file_input -> stmt -> compound_stmt -> (decorated ->) funcdef -> COLON
    compound_stmt = st_tuple[1][1]
    if compound_stmt[1][0] == symbol.decorated:
        funcdef = compound_stmt[1][2]
    else:
        funcdef = compound_stmt[1]
    colon = funcdef[4]
    colon_lineno = colon[2]

    body_start_lineno = colon_lineno + 1
    body_source_lines = source.splitlines()[body_start_lineno - 1 :]
    body_source = "\n".join(body_source_lines)

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
