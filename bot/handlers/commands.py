# Bot command handlers

import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from bot.api.client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("bot")

router = Router()

@router.message(Command('start'))
async def welcome(msg: Message):
    user_id = msg.from_user.id
    user_name = msg.from_user.username

    user = await APIClient.upsert_user(user_id, user_name)
    if not user: 
        logger.error(f"The {user_name} was not saved in database")

    welcome_text = (
        f"Hi {user_name}!\n\n"
        "⚡️🌤️ <b>SkySentry</b> - Automated weather tracking tool and there's the opportunity make weather schedules for any time and world destination! 🗺️⌚\n\n"
        "Available commands:\n"
        "\t📍 /set_city\n"
        "\t⏰ /set_schedule\n"
        "\t📊 /now\n"
        "\tℹ️ /help — Show guidance"
    )

    await msg.answer(
        text=welcome_text,
        parse_mode="HTML"
    )

@router.message(Command('help'))
async def help(msg: Message):
    help_text = (
        "📖 <b>SkySentry Quick Guide:</b>\n\n"
        "1. First, use <b>/set_city</b> to save your destination.\n"
        "2. Use <b>/now</b> anytime to get an instant breakdown of the weather.\n"
        "3. Use <b>/set_schedule</b> to create a daily broadcast at your chosen time."
    )
    await msg.answer(text=help_text, parse_mode="HTML")