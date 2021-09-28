__all__ = ["tk_is_available"]


def tk_is_available() -> bool:
    """Check if Tk is available"""

    try:
        import tkinter  # type: ignore
    except ModuleNotFoundError:
        return False
    else:
        return True
