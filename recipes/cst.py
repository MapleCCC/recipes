import libcst as cst
import libcst.matchers


__all__ = ["contains_outdented_comment", "transform_source"]


def contains_outdented_comment(node: cst.CSTNode) -> bool:
    """
    Return `True` if the concrete syntax tree represented by the CST node contains
    outdented comments, and `False` otherwise.
    """

    m = libcst.matchers
    return bool(m.findall(node, m.EmptyLine(indent=False, comment=m.Comment())))


def transform_source(transformer: cst.CSTTransformer, source: str) -> str:
    """Transform the source code with the cst node transformer"""

    module = cst.parse_module(source)
    new_module = module.visit(transformer)
    return new_module.code
