# Bot Handlers

import logging

from aiogram import BaseMiddleware, Router
from aiogram.types import Message, TelegramObject
from aiogram.filters import Command

from database.db_engines import sessionmaker

from typing import Callable, Any, Dict, Awaitable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: Any):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        async with self.session_pool() as session:
            data["session"] = session 
            return await handler(event, data)


router = Router()

# Database Session Middleware registrate
router.message.middleware(DbSessionMiddleware(sessionmaker))

@router.message(Command('start'))
async def welcome(msg: Message):
    await msg.answer(
        text=... # the message will be 
    )
