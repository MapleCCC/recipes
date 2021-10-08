import ast


__all__ = ["transform_source"]


def transform_source(transformer: ast.NodeTransformer, source: str) -> str:
    """Transform the source code with the node transformer"""

    # FIXME ast.parse/unparse doesn't preserve some details of the source code
    #     implicitly converts double quotes to single quotes
    #     doesn't preserve comments
    #     doesn't preserve some whitespaces such as the trailing newline
    # Solution: use concrete syntax tree library

    syntax_tree = ast.parse(source)
    new_syntax_tree = transformer.visit(syntax_tree)
    new_source = ast.unparse(ast.fix_missing_locations(new_syntax_tree))
    return new_source
