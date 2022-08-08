__all__ = ["line_boundaries", "beginswith"]


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


# Supplanted by `str.startswith()`
def beginswith(s: str, prefix: str) -> bool:
    """ Inverse of the `str.endswith` method """
    return s[: len(prefix)] == prefix
