import inspect
import parser
from types import FunctionType
from typing import cast

from .sourcelib import unindent_source


__all__ = ["get_function_body_source"]


# FIXME typeshed bug STType.totuple() -> Tuple[Any, ...]

# FIXME It is quite insane to use a sequence of magic numbers to inspect syntax tree.
#     Let's use an object-oriented concrete syntax tree library instead.


def get_function_body_source(func: FunctionType) -> str:
    """
    Retrieve source code of the body of the function.
    """

    # 1. Retrieve source code of the function, which is then parsed into concrete syntax
    # tree.
    #
    # 2. Inspect the concrete syntax tree, and locate the position of the colon token
    # which marks the delimitation between function header and function body.
    #
    # 3. Extract the source code of function body after the source line of the colon
    # token.

    source = inspect.getsource(func)

    syntax_tree = parser.suite(unindent_source(source))

    # Convert syntax tree to tuple representation
    st_tuple = cast(tuple, syntax_tree.totuple(line_info=True))

    # Locate the colon token that marks the delimitations between function header and
    # function body.
    #
    # Node chain: file_input -> stmt -> compound_stmt -> funcdef -> COLON
    colon = st_tuple[1][1][1][4][3]
    colon_lineno = colon[3]

    body_start_lineno = colon_lineno + 1
    body_source_lines = source.splitlines()[body_start_lineno - 1 :]
    body_source = "\n".join(body_source_lines)

    return body_source
