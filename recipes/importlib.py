import importlib
import importlib.util
from types import ModuleType

from .functools import lazy_call


__all__ = ["importable", "lazy_import_module"]


def importable(module: str) -> bool:
    """Check if a module is importable."""

    # Reference: https://docs.python.org/3/library/importlib.html#checking-if-a-module-can-be-imported

    return importlib.util.find_spec(module) is not None


# Refer to the comments of `lazy_call()` for explanation of the type annotation design.
def lazy_import_module(name: str, package: str = None) -> ModuleType:
    """Lazy version of `importlib.import_module()`"""

    return lazy_call(importlib.import_module, name, package)
