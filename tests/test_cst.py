import libcst as cst

from recipes.cst import contains_outdented_comment, transform_source


def test_contains_outdented_comment() -> None:

    source = "def f():\n    a = 1\n    b = 2\n"
    module = cst.parse_module(source)
    assert not contains_outdented_comment(module)

    source = "def f():\n    a = 1\n# Foo bar\n    b = 2\n"
    module = cst.parse_module(source)
    assert contains_outdented_comment(module)


def test_transform_source() -> None:

    source = "a = 1\nb = 2\n"

    class IncrementIntegerLiteral(cst.CSTTransformer):
        def leave_Integer(
            self, original_node: cst.Integer, updated_node: cst.Integer
        ) -> cst.Integer:
            new_integer = str(updated_node.evaluated_value + 1)
            return updated_node.with_changes(value=new_integer)

    assert transform_source(IncrementIntegerLiteral(), source) == "a = 2\nb = 3\n"
