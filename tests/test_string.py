from recipes.string import line_boundaries


def test_line_boundaries() -> None:
    for b in line_boundaries:
        assert str.splitlines(b) == [""]
