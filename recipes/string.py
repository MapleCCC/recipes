__all__ = ["line_boundary"]


# A string containing characters considered line boundaries
# Reference: https://docs.python.org/3.9/library/stdtypes.html#str.splitlines
line_boundary = "\n\r\v\x0b\f\x0c\x1c\x1d\x1e\x85\u2028\u2029"
