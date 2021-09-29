from .constants import MAX_INT


__all__ = ["unindent_source"]


def is_blank_line(line: str) -> bool:
    return not line.strip()


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def is_source_line(line: str) -> bool:
    return not is_blank_line(line) and not is_comment_line(line)


def indent_level(line: str) -> int:
    """Get the indentation level of given line"""

    return len(line) - len(line.lstrip())


def unindent_source(text: str, *, reflow_comments: bool = True) -> str:
    """
    Unindent the source code.

    By default, comments are reflowed such that they are justified to match the level of
    their surrounding blocks. The reflow behavior can be turned off by setting the
    `reflow_comments` parameter to `False`.
    """

    lines = text.splitlines()

    if not lines:
        return text

    if not reflow_comments:
        # Easy implementation where comments are treated verbatim
        margin = min(len(line) - len(line.lstrip()) for line in lines if line.strip())

        if not margin:
            return text

        return "\n".join(line[margin:] for line in lines)

    # Long implementation that reflows comments

    margin = MAX_INT
    for line in lines:
        if is_source_line(line):
            margin = min(margin, indent_level(line))

    if not margin:
        return text

    new_lines = []
    for line in lines:
        if is_source_line(line):
            new_lines.append(line[margin:])
        else:
            new_lines.append(line.lstrip())

    return "\n".join(new_lines)
