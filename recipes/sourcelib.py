from .exceptions import Unreachable


__all__ = ["OutdentedCommentError", "unindent_source"]


def is_blank_line(line: str) -> bool:
    return not line.strip()


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def is_source_line(line: str) -> bool:
    return not is_blank_line(line) and not is_comment_line(line)


def indent_level(line: str) -> int:
    """Get the indentation level of given line"""

    return len(line) - len(line.lstrip())


class OutdentedCommentError(Exception):
    "Raised when `unindent_source()` encounters outdented comments"


def unindent_source(text: str, *, reflow_comments: bool = False) -> str:
    """
    Unindent the source code.

    Outdented comments cause `OutdentedCommentError` to get raised. This could be
    mitigated by setting the `reflow_comments` parameter to `True`, to reflow comments
    such that they are justified to match the level of their surrounding blocks.
    """

    lines = text.splitlines()
    if not lines:
        return text

    margin = min(indent_level(line) for line in lines if is_source_line(line))
    if not margin:
        return text

    new_lines = []

    for line in lines:

        if is_source_line(line) or is_blank_line(line):
            new_lines.append(line[margin:])

        elif is_comment_line(line):
            if reflow_comments:
                new_lines.append(line.lstrip())

            elif indent_level(line) >= margin:
                new_lines.append(line[margin:])

            else:
                error_message = "can't unindent source code with outdented comments"
                raise OutdentedCommentError(error_message)

        else:
            raise Unreachable

    return "\n".join(new_lines)
