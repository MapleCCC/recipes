import re
import sys

import pytest

from recipes.exceptions import OutdentedCommentError
from recipes.inspect import get_function_body_source


class TestGetFunctionBodySource:
    def test_normal_case(self) -> None:
        def f():
            a = 1
            b = 2

        assert get_function_body_source(f) == "a = 1\nb = 2\n"

    def test_lambda(self) -> None:
        assert get_function_body_source(lambda: 321) == "321"

    def test_method(self) -> None:
        class A:
            def b(self):
                a = 1
                b = 2

        assert get_function_body_source(A.b) == "a = 1\nb = 2\n"
        assert get_function_body_source(A().b) == "a = 1\nb = 2\n"

    # fmt: off
    # temporarily disable black formatter, so that we can test the case with outdented comments.
    def test_function_with_outdented_comments(self) -> None:
        def f():
            a = 1
          # foo bar
            b = 2

        with pytest.raises(
            OutdentedCommentError,
            match=re.escape(
                "get_function_body_source() expects no outdented comments in the body of the function"
            ),
        ):
            get_function_body_source(f)
    # fmt: on

    def test_invalid_argument(self) -> None:

        with pytest.raises(ValueError):
            get_function_body_source(len)

        with pytest.raises(ValueError):
            get_function_body_source(sys.exit)

        with pytest.raises(ValueError):
            get_function_body_source(TestGetFunctionBodySource)
