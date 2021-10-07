import re
import sys

import pytest

from recipes.contextlib import literal_block, skip_context
from recipes.exceptions import OutdentedCommentError


def test_skip_context() -> None:

    a = 0
    with skip_context():
        a = 1
    assert a == 0


class TestLiteralBlock:
    """Unit tests for `literal_block()`"""

    def test_context_manager(self) -> None:

        with literal_block() as source:
            a = 1
            b = 2

        assert source == "a = 1\nb = 2\n"

        with pytest.raises(NameError):
            _ = a

    def test_decorator(self) -> None:
        @literal_block
        def source():
            a = 1
            b = 2

        assert source == "a = 1\nb = 2\n"

        with pytest.raises(NameError):
            _ = a

    def test_decorator_with_formatting(self) -> None:

        c = 3

        @literal_block
        def source(c):
            a = 1
            b = c

        assert source == "a = 1\nb = 3\n"

        with pytest.raises(NameError):
            _ = a

    def test_decorator_with_formatting_and_fallback(self) -> None:
        @literal_block
        def source(d=4):
            a = 1
            b = d

        assert source == "a = 1\nb = 4\n"

        with pytest.raises(NameError):
            _ = a

    def test_invalid_argument(self) -> None:

        with pytest.raises(ValueError, match="expect a user-defined function"):
            literal_block(len)

        with pytest.raises(ValueError, match="expect a user-defined function"):
            literal_block(sys.exit)

        with pytest.raises(ValueError, match="expect a user-defined function"):
            literal_block(TestLiteralBlock)

    def test_decorator_with_no_replacement_found(self) -> None:

        with pytest.raises(NameError, match="has no replacement found"):

            @literal_block
            def source(c):
                a = 1
                b = c

    # fmt: off
    # temporarily disable black formatter, so that we can test the case with outdented comments.
    def test_context_manager_with_outdented_comment(self) -> None:

        with pytest.raises(
            OutdentedCommentError,
            match=re.escape(
                "the block in the body of literal_block() should not contain outdented comments"
            ),
        ):

            with literal_block() as source:
                a = 1
              # foo bar
                b = 2
    # fmt: on

    # fmt: off
    # temporarily disable black formatter, so that we can test the case with outdented comments.
    def test_decorator_with_outdented_comment(self) -> None:

        with pytest.raises(
            OutdentedCommentError,
            match= "@literal_block expects no outdented comments in the body of the decorated function"
        ):

            @literal_block
            def source():
                a = 1
              # foo bar
                b = 2
    # fmt: on
