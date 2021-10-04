import pytest

from recipes.builtins import hashable


def test_hashable() -> None:

    assert hashable(1)
    assert hashable(1.0)
    assert hashable(None)
    assert hashable(True)
    assert hashable("")
    assert hashable(globals)
    assert hashable(exec)
    assert hashable(ValueError)

    assert not hashable([])
    assert hashable(tuple())
    # test hashability of dict
    assert not hashable({})
    # test hashability of set
    assert not hashable({1})

    def func():
        pass

    class A:
        pass

    assert hashable(func)
    assert hashable(A)
    assert hashable(A())

    assert hashable(hashable)

    assert hashable(pytest)

    assert hashable(test_hashable)
