import pytest

from recipes.sourcelib import OutdentedCommentError, unindent_source


class TestUnindentSource:
    def test_nomral_case(self) -> None:
        source = "    a = 1\n    b = 2\n"
        assert unindent_source(source) == "a = 1\nb = 2\n"

    def test_nested_levels(self) -> None:
        source = "    a = 1\n        b = 2\n"
        assert unindent_source(source) == "a = 1\n    b = 2\n"

    def test_with_blank_line(self) -> None:
        source = "    a = 1\n    \n    b = 2\n"
        assert unindent_source(source) == "a = 1\n\nb = 2\n"
        source = "    a = 1\n     \n    b = 2\n"
        assert unindent_source(source) == "a = 1\n \nb = 2\n"
        source = "    a = 1\n  \n    b = 2\n"
        assert unindent_source(source) == "a = 1\n\nb = 2\n"

    def test_with_comment(self) -> None:
        source = "    a = 1\n    # Foo bar\n    b = 2\n"
        assert unindent_source(source) == "a = 1\n# Foo bar\nb = 2\n"
        source = "    a = 1\n       # Foo bar\n    b = 2\n"
        assert unindent_source(source) == "a = 1\n   # Foo bar\nb = 2\n"

    def test_with_outdented_comment(self) -> None:
        source = "    a = 1\n# Foo bar\n    b = 2\n"
        with pytest.raises(OutdentedCommentError):
            unindent_source(source)

    def test_reflow_comment(self) -> None:
        source = "    a = 1\n# Foo bar\n    b = 2\n"
        assert (
            unindent_source(source, reflow_comments=True) == "a = 1\n# Foo bar\nb = 2\n"
        )
        source = "    a = 1\n             # Foo bar\n    b = 2\n"
        assert (
            unindent_source(source, reflow_comments=True) == "a = 1\n# Foo bar\nb = 2\n"
        )
