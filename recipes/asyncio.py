from __future__ import annotations  # for types imported from _typeshed

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from functools import wraps
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, TypeVar, ParamSpec

from .builtins import read_text, write_text


if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath, StrPath


__all__ = [
    "asyncio_subprocess_check_output",
    "aread_text",
    "awrite_text",
    "asyncio_run",
]


P = ParamSpec("P")
R = TypeVar("R")


async def asyncio_subprocess_check_output(
    args: Sequence[StrOrBytesPath], redirect_stderr_to_stdout: bool = False
) -> bytes:
    """Augment `subprocess.check_output()` with async support"""

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT if redirect_stderr_to_stdout else None,
    )
    stdout, stderr = await proc.communicate()

    retcode = proc.returncode
    assert retcode is not None

    if retcode != 0:
        raise CalledProcessError(retcode, args, stdout, stderr)

    return stdout


async def aread_text(file: StrPath, encoding: str = "utf-8") -> str:
    """
    Asynchronously read text in UTF-8 encoding.

    This is mostly a convenient wrapper to reduce the boilerplate of `open()` and
    `Path.read_text()`. The caller doesn't need to specify the `"r"` and `"t"` flags and
    doesn't need to explicitly specify `encoding="utf-8"` in platforms where
    `locale.getpreferredencoding()` doesn't return "UTF-8".
    """

    return await asyncio.to_thread(read_text, file, encoding)


async def awrite_text(file: StrPath, text: str, encoding: str = "utf-8") -> None:
    """
    Asynchronously write text in UTF-8 encoding.

    This is mostly a convenient wrapper to reduce the boilerplate of `open()` and
    `Path.write_text()`. The caller doesn't need to specify the `"w"` and `"t"` flags
    and doesn't need to explicitly specify `encoding="utf-8"` in platforms where
    `locale.getpreferredencoding()` doesn't return "UTF-8".
    """

    return await asyncio.to_thread(write_text, file, text, encoding)


def asyncio_run(func: Callable[P, Awaitable[R]]) -> Callable[P, R]:
    """Make an async function sync, by wrapping it inside `asyncio.run()` call"""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(func(*args, **kwargs))

    return wrapper
