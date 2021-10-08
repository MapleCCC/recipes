import ast

from recipes.ast import transform_source


def test_transform_source() -> None:
    source = "a = 1\nb = 2"

    class IncrementIntegerLiteral(ast.NodeTransformer):
        def visit_Constant(self, node: ast.Constant) -> ast.Constant:
            if isinstance(node.value, int):
                node.value += 1
            return node

    assert transform_source(IncrementIntegerLiteral(), source) == "a = 2\nb = 3"
