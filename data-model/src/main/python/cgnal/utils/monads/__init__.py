import asyncio
from functools import wraps
from typing import Callable, Awaitable

from pymonad.promise import Promise, _Promise

from cgnal.utils.monads.either import Either, Right, Left


def safe(f: Callable) -> Callable:
    """
    Transform any function in a safe counterpart, where raised exceptions are encampsulated with the Left monad.
    :param f: function
    :return: wrapper function that returns a Either object
    """

    @wraps(f)
    def wrap(*args, **kwargs) -> Either:
        try:
            return Right(f(*args, **kwargs))
        except Exception as e:
            return Left(e)

    return wrap


def async_func(func: Callable) -> Callable:
    """
    Transform simple function in async function using promises
    :param func: simple function
    :return: async function
    """

    async def getArgs(args):
        return await asyncio.gather(
            *[arg if isinstance(arg, Awaitable) else Promise.insert(arg) for arg in args]
        )

    async def getKwargs(kwargs):
        kwargsTasks = [arg.map(lambda x: (ith, x)) if isinstance(arg, Awaitable) else Promise.insert((ith, arg))
                       for ith, arg in kwargs.items()]
        return dict(await asyncio.gather(*kwargsTasks))

    async def async_wrap(*args, **kwargs):
        (_args, _kwargs) = await asyncio.gather(getArgs(args), getKwargs(kwargs))

        return func(*_args, **_kwargs)

    def wrapper(*args, **kwargs):
        return _Promise(lambda resolve, reject: async_wrap(*args, **kwargs), None)

    return wrapper
