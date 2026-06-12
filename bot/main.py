# Main start file

import asyncio
import logging
from aiogram import Bot, Dispatcher

from bot.config import settings

from bot.handlers import router as commands_router

if not settings.BOT_TOKEN:
    raise ValueError("There's no the bot token in .env file.")

bot = Bot(settings.BOT_TOKEN)

dp = Dispatcher()

dp.include_router(commands_router)

async def main():

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("The bot work is stopping...")