import pytest

from recipes.exceptions import OutdentedCommentError
from recipes.sourcelib import unindent_source


class TestUnindentSource:
    def test_nomral_case(self) -> None:
        source = "    a = 1\n    b = 2\n"
        assert unindent_source(source) == "a = 1\nb = 2\n"

    def test_nested_levels(self) -> None:
        source = "    a = 1\n        b = 2\n"
        assert unindent_source(source) == "a = 1\n    b = 2\n"

    def test_empty_input(self) -> None:
        source = "     "
        assert unindent_source(source) == source
        source = "     \n"
        assert unindent_source(source) == source

    def test_no_indentation(self) -> None:
        source = "a = 1\nb = 2\n"
        assert unindent_source(source) == source
        source = "a = 1\n   b = 2\n"
        assert unindent_source(source) == source

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

    def test_preserve_newline(self) -> None:
        source = "    a = 1\r\n    b = 2\n"
        assert unindent_source(source) == "a = 1\r\nb = 2\n"
        source = "    a = 1\n    \r\n    b = 2\n"
        assert unindent_source(source) == "a = 1\n\r\nb = 2\n"
        source = "    a = 1\n  \r\n    b = 2\n"
        assert unindent_source(source) == "a = 1\n\r\nb = 2\n"
