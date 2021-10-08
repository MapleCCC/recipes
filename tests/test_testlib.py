import _pytest.outcomes
import pytest

from recipes.testlib import pytest_fail_without_context


def test_pytest_fail_without_context() -> None:

    with pytest.raises(_pytest.outcomes.Failed) as exc_info:
        pytest_fail_without_context()

    assert exc_info.value.__context__ is None
