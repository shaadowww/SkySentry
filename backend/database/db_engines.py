# Technical Part of Database

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.config import settings

engine = create_async_engine(
    settings.DB_URL,
    # echo=True
)

sessionmaker = async_sessionmaker(engine, expire_on_commit=False) 

class Base(DeclarativeBase):
    ...