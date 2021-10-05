__all__ = ["Unreachable", "OutdentedCommentError"]


class Unreachable(RuntimeError):
    """Raised when supposedly unreachable code is reached"""


class OutdentedCommentError(Exception):
    """Raised when outdented comments are detected"""
