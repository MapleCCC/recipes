from hypothesis import given, strategies as st

from recipes.string import line_boundaries, remove_leading_newline


def test_line_boundaries() -> None:
    for b in line_boundaries:
        assert str.splitlines(b) == [""]


@given(st.sampled_from(line_boundaries), st.text())
def test_remove_leading_newline(line_boundary: str, text: str) -> None:
    new_text = line_boundary + text
    assert remove_leading_newline(new_text) == text
