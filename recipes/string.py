__all__ = ["line_boundaries", "remove_leading_newline"]


# A collection of strings considered line boundaries
# Reference: https://docs.python.org/3.9/library/stdtypes.html#str.splitlines
line_boundaries = [
    "\n",
    "\r",
    "\r\n",
    "\v",
    "\x0b",
    "\f",
    "\x0c",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
]


def remove_leading_newline(string: str) -> str:
    """Remove the leading newline"""

    for newline in sorted(line_boundaries, key=len, reverse=True):
        if string.startswith(newline):
            return string.removeprefix(newline)

    return string
