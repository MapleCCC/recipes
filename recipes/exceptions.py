__all__ = ["Unreachable", "OutdentedCommentError"]


# XXX whether to inherit from `RuntimeError` or `Exception` ?
class Unreachable(RuntimeError):
    """
    Raised when supposedly unreachable code is reached

    Some branch is theoretically unreachable, but surprisingly jumped in.

    Alternative to `raise Unreachable` is to either `raise`ValueError` or `typing.assert_never()`.

    1. When the unreachability is up to a user-supplied argument, choose `raise ValueError`.
    2. When the unreachability is provable by type checker, choose `typing.assert_never()`.
    3. When the unreachability is unprovable by type checker, choose `raise Unreachable`.

    Reference: https://typing.readthedocs.io/en/latest/source/unreachable.html
    """


class OutdentedCommentError(Exception):
    """Raised when outdented comments are detected"""
