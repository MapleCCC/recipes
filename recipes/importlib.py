import importlib
from functools import partial
from types import ModuleType
from typing import cast

from lazy_object_proxy import Proxy


__all__ = ["lazy_import_module"]


def lazy_import_module(name: str, packge: str = None) -> ModuleType:
    """Lazy version of `importlib.import_module()`"""

    lazy_module = Proxy(partial(importlib.import_module, name, packge))
    return cast(ModuleType, lazy_module)
