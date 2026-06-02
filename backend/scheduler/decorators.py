from backend.database.db_engines import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps

async def get_session(func: callable):
    '''
    Decorator to receive session
    '''
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