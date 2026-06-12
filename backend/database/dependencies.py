from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.db_engines import sessionmaker

async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session Generator for FastAPI Depends
    """
    async with sessionmaker() as session:
        yield session