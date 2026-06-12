# Bot command handlers

import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(asctime)s] - %(message)s",
    datefmt="%H:%M:%S"
)

router = Router()

@router.message(Command('start'))
async def welcome(msg: Message):

    welcome_text = (
        "Hi!\n\n"
        "⚡️🌤️ <b>SkySentry</b> - Automated weather tracking tool and there's the opportunity make weather schedules for any time and world destination! 🗺️⌚\n\n"
        "Available commands:\n"
        "\t{pass}" # here the commands will be
    )

    await msg.answer(
        text=welcome_text,
        parse_mode="HTML"
    )

@router.message(Command(''))
async def help(msg: Message):
    pass