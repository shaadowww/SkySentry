# Main start file

import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher

from bot.config import settings

from bot.handlers import router as routers
from bot.api.client import APIClient

if not settings.BOT_TOKEN:
    raise ValueError("There's no the bot token in .env file.")

bot = Bot(settings.BOT_TOKEN)

dp = Dispatcher()

dp.include_router(routers)

async def main():
    http_client = httpx.AsyncClient()
    APIClient.client = http_client
    logging.info("Telegram Bot connection pool initialized. Starting pooling...")
    
    try:
        await dp.start_polling(bot)
    finally:
        logging.info("🔴 Closing HTTPX connection pool...")
        await http_client.aclose()
        logging.info("🛑 Bot has been successfully stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("The bot work is stopping...")