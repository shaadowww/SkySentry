from backend.database.db_engines import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps
from collections.abc import Callable, Awaitable
from typing import Any

def session_deco(func: Callable[..., Awaitable[Any]]):
    """
    Decorator to automatically inject a database session into the function kwargs.

    Example of injected argument:
    ```python
    kwargs['session'] = session
    ```
    The target function must receive a `session: AsyncSession` argument.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        session_in_args = any(isinstance(arg, AsyncSession) for arg in args)
        session_in_kwargs = 'session' in kwargs

        if session_in_args or session_in_kwargs:
            return await func(*args, **kwargs)
        
        async with sessionmaker() as session:
            kwargs['session'] = session
            return await func(*args, **kwargs)
    return wrapper