from .constants import MAX_INT


__all__ = ["unindent_source"]


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
        unindented = line.lstrip()
        if not unindented or unindented.startswith("#"):
            continue
        margin = min(margin, len(line) - len(unindented))

    if not margin:
        return text

    new_lines = []
    for line in lines:
        unindented = line.lstrip()
        if unindented.startswith("#"):
            new_lines.append(unindented)
        else:
            new_lines.append(line[margin:])

    return "\n".join(new_lines)
