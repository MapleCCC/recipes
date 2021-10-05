import re

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

    def test_normal_case(self) -> None:

        with literal_block() as source:
            a = 1
            b = 2

        assert source == "a = 1\nb = 2\n"

    # fmt: off
    # temporarily disable black formatter, so that we can test the case with outdented comments.
    def test_wiht_outdented_comment(self) -> None:

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
