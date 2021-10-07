from hypothesis import given, strategies as st

from recipes.constants import MAX_INT


@given(st.integers())
def test_max_int(x: int) -> None:
    assert MAX_INT > x
