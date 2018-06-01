from typing import (
    Callable, TypeVar, Any
)
from types import (
    CoroutineType, FunctionType, GeneratorType
)
from collections.abc import Iterator
from asyncio import Task

import asyncio
from functools import partial, singledispatch


A = TypeVar('A')
B = TypeVar('B')


def compose(f : Callable[[A], B],
            g : Callable[..., A] = None,
            ) -> Callable[..., B]:
    if not g:
        return partial(compose, f)
    return lambda *args, **kwargs: f(g(*args, **kwargs))


def fmap(f   : Callable,
         obj : Any = None,
         ) -> Any:
    if obj is None:
        return partial(fmap, f)
    return _fmap(obj, f)


@singledispatch
def _fmap(obj, f):  # type: ignore
    return obj.fmap(f)


@_fmap.register(list)
def _(obj, f):
    return [f(el) for el in obj]


@_fmap.register(tuple)  # type: ignore
def _(obj, f):
    return tuple(f(el) for el in obj)


@_fmap.register(CoroutineType)  # type: ignore
def _(obj, f):
    async def wrapped():
        return f(await obj)
    return wrapped()


@_fmap.register(Task)  # type: ignore
def _(obj, f):
    async def wrapped():
        return f(await obj)
    return asyncio.ensure_future(wrapped())


@_fmap.register(GeneratorType)  # type: ignore
def _(obj, f):
    return (f(el) for el in obj)


@_fmap.register(Iterator)  # type: ignore
def _(obj, f):
    return map(f, obj)


@_fmap.register(FunctionType)  # type: ignore
def _(obj, f):
    return compose(f, obj)
