import importlib
import importlib.util
from functools import partial
from types import ModuleType
from typing import cast

from lazy_object_proxy import Proxy


__all__ = ["importable", "lazy_import_module"]


def importable(module: str) -> bool:
    """Check if a module is importable."""

    # Reference: https://docs.python.org/3/library/importlib.html#checking-if-a-module-can-be-imported

    return importlib.util.find_spec(module) is not None


def lazy_import_module(name: str, packge: str = None) -> ModuleType:
    """Lazy version of `importlib.import_module()`"""

    lazy_module = Proxy(partial(importlib.import_module, name, packge))
    return cast(ModuleType, lazy_module)
