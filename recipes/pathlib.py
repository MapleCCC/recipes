import os
from pathlib import Path


__all__ = ["canonicalize_path"]


def canonicalize_path(path: Path) -> Path:

    # 1. Tilde expansion
    path = path.expanduser()

    # 2. Make absolute path, and resolve symlinks
    path = path.resolve()

    # 3. On Windows, paths are case insensitive
    if os.name == "nt":
        path = Path(*(part.lower() for part in path.parts))

    return path
