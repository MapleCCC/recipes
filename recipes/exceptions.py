__all__ = ["Unreachable"]


class Unreachable(RuntimeError):
    """Raised when supposedly unreachable code is reached"""
