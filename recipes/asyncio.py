from __future__ import annotations  # for types imported from _typeshed

import asyncio
from collections.abc import Sequence
from subprocess import CalledProcessError
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath


__all__ = ["asyncio_subprocess_check_output"]


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
