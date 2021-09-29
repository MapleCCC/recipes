from typing import NoReturn

import pytest

from .exceptions import Unreachable


__all__ = ["pytest_fail_without_context"]


def pytest_fail_without_context(msg: str = "", pytrace: bool = True) -> NoReturn:
    """Similar to pytest.fail(), but with context eliminated."""

    __tracebackhide__ = True

    try:
        pytest.fail(msg, pytrace)

    # pytest doesn't expose `_pytest.outcomes.Failed` as public API, and it would be
    # fragile to rely on private API, hence discouraged. Current naive workaround is to
    # blindly and greedily catch any exceptions.
    except BaseException as exc:
        raise exc from None

    raise Unreachable
