from collections.abc import Iterator
from pathlib import Path

from pathspec import PathSpec


__all__ = ["gitignore_aware_os_walk"]


EmptyPathSpec = PathSpec([])


def gitignore_aware_os_walk(
    path: Path,
    pathspec: PathSpec = EmptyPathSpec,
    aggressive: bool = False,
) -> Iterator[Path]:

    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")

    local_gitignore = path / ".gitignore"

    if local_gitignore.is_file():

        lines = local_gitignore.read_text(encoding="utf-8").splitlines()

        if aggressive:
            lines.extend([".git/", ".gitignore"])

        local_pathspec = PathSpec.from_lines("gitwildmatch", lines)

        pathspec += local_pathspec

    for child in path.iterdir():

        if child.is_file():

            if not pathspec.match_file(child):
                yield child

        elif child.is_dir():

            # WARNING: gitignore pattern can be specialized for directory if a ending
            # separator exists [1]. It's therefore necessary to transform a directory
            # from Path("foo") to "foo/", so that `pathspec.match_file()` can
            # distinguish between file and directory.
            #
            # Reference:
            # [1] "If there is a separator at the end of the pattern then the pattern
            #     will only match directories, otherwise the pattern can match both
            #     files and directories."
            #     Source: https://git-scm.com/docs/gitignore#_pattern_format

            if not pathspec.match_file(str(child) + "/"):
                yield from gitignore_aware_os_walk(child, pathspec, aggressive)

        else:
            raise RuntimeError("Unexpected condition")
