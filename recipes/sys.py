from .importlib import importable


__all__ = ["tk_is_available"]


def tk_is_available() -> bool:
    """Check if Tk is available"""

    return importable("tkinter")
