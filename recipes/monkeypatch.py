from collections.abc import Callable, Iterator, Sequence
from contextlib import AbstractContextManager, ExitStack, contextmanager
from functools import partial
from typing import Any

from .builtins import getattr_r, setattr_r
from .functools import inject_pre_hook as plain_inject_pre_hook


__all__ = ["setattr", "mapattrs", "inject_pre_hook"]


@contextmanager
def mp_setattr(obj: object, attr: str, value: object) -> Iterator[None]:

    orig_value = getattr_r(obj, attr)
    setattr_r(obj, attr, value)

    try:
        yield
    finally:
        setattr_r(obj, attr, orig_value)


@contextmanager
def mp_mapattrs(
    func: Callable[[Any], Any], obj: object, attrs: Sequence[str]
) -> Iterator[None]:

    with ExitStack() as stack:
        for attr in attrs:
            new_attr = func(getattr(obj, attr))
            ctx = mp_setattr(obj, attr, new_attr)
            stack.enter_context(ctx)
        yield


def mp_inject_pre_hook(
    pre: Callable[..., None], obj: object, methods: list[str]
) -> AbstractContextManager[None]:
    return mp_mapattrs(partial(plain_inject_pre_hook, pre), obj, methods)


# Export simple names for use in qualified manner
#
# Such as:
# ```
# import monkeypatch as mp
# with mp.setattr(user, name, "John"):
#     register_account(user.name)
# ```

setattr = mp_setattr
mapattrs = mp_mapattrs
inject_pre_hook = mp_inject_pre_hook
