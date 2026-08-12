# Bot command handlers

import logging
import datetime 

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery

from bot.api.client import APIClient
from bot.keyboards import settings_output

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
    assert msg.from_user is not None
    
    user_id = msg.from_user.id 
    user_name = msg.from_user.username 

    user = await APIClient.upsert_user(user_id, user_name)
    if not user: 
        logger.error(f"The {user_name} was not saved in database")

    welcome_text = (
        f"Hi {user_name}!\n\n"
        "⚡️🌤️ <b>SkySentry</b> - Automated weather tracking tool and there's the opportunity make weather schedules for any time and world destination! 🗺️⌚\n\n"
        "Available commands:\n"
        "\t📍 /set_city - Setting your city in configuration for weather forecasts\n"
        "\t⏰ /set_schedule - Setting the weather schedule you prefer\n"
        "\t📊 /now - Get the weather <b>now</b>\n"
        "\t🌆☁️ /city_weather - Receive the weather information in specified city or coordinates\n"
        "\t🌡️ /daily - Receive Daily Weather Forecast\n"
        "\tℹ️ /help — Show guidance\n"
        "\t⚙️ /settings - Receive your saved configurations\n"
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
        "3. Use <b>/set_schedule</b> to create a daily broadcast at your chosen time.\n"
        "Also, you can use <b>/settings</b> to check your saved local configurations."
    )
    await msg.answer(text=help_text, parse_mode="HTML")

@router.message(Command('settings'))
async def settings_cmd(msg: Message, state: FSMContext):
    """Receive your saved configurations"""
    assert msg.from_user is not None
    text_response: str = (
        "🛠️ <b>SkySentry Configuration</b>\n\n"
    )

    ulocation: dict | None = await APIClient.get_location(msg.from_user.id)

    uschedules: list[dict] | None = await APIClient.get_user_schedules(msg.from_user.id)

    if "error" in ulocation:
        await msg.answer(
            text=(
                "🛠️ <b>SkySentry Configuration</b>\n\n"
                "📍 <b>Your location:</b>\n"
                "\n⚠️ You have no the saved location in configuration.\n\n"
                "📅 <b>Your Schedules:</b>\n"
                "\n⚠️ You have no any schedule."
            ),
            parse_mode="HTML",
            reply_markup=settings_output(has_city=False, has_schedules=False)
        )
        return

    city_name: str = ulocation.get("city_name", " ")
    latitude: float = ulocation.get("latitude")
    longitude: float = ulocation.get("longitude")

    location_output: str = (
        "📍 <b>Your location:</b>\n"
        f"🗺️ <b>City:</b> {city_name}\n"
        f"🌐 <b>Latitude:</b> <code>{latitude}</code>\n"
        f"🌐 <b>Longitude</b>: <code>{longitude}</code>\n\n"
    )
    text_response += location_output

    schedules_output: str = (
        "📅 <b>Your Schedules:</b>\n"
    )

    if uschedules is None or len(uschedules) == 0:
        text_response += (
            "📅 <b>Your Schedules:</b>\n"
            "\n⚠️ You have no any schedule."
        )
        await msg.answer(
            text_response,
            parse_mode="HTML",
            reply_markup=settings_output(has_schedules=False)
        )
        return

    schedules_list: str = ""
    user_schedule_data: dict = {}

    for ind, schedule in enumerate(uschedules):
        city = schedule.get("city")
        time: datetime.time = schedule.get("time")

        result = (
            f"<b>Schedule</b> #{ind + 1}\n"
            f"- City: <b>{city}</b>\n"
            f"- Time: <code>{time}</code> everyday\n\n"
        )
        time_str = time.strftime("%H:%M") if hasattr(time, "strftime") else str(time)[:5]
        user_schedule_data[f"{ind + 1}"] = {"city": city, "time": time_str}
        schedules_output += result
        schedules_list += result

    text_response += schedules_output

    await state.update_data(
        us_schedule_data=user_schedule_data,
        all_schedules_result=schedules_list
    )
    
    
    await msg.answer(
        text_response, 
        parse_mode="HTML",
        reply_markup=settings_output()
    )

@router.callback_query(F.data == "  ")
async def process_empty(callback: CallbackQuery):
    """Processing the empty button"""
    await callback.answer()
    return