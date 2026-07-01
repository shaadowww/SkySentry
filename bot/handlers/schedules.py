# Schedule Handler 
import datetime
from timezonefinder import TimezoneFinder

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.states import SetupStates
from bot.keyboards import cancel_keyboard
from bot.api.client import APIClient

router = Router()

@router.message(Command('set_schedule'))
async def set_schedule(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    user_location = await APIClient.get_location(user_id)

    if not user_location or "error" in user_location:
        await msg.answer(
            "⚠️ You haven't configured your city yet!\n"
            "Please use the <b>/set_city</b> command first before setting up a schedule",
            parse_mode="HTML"
        )
        return

    city_name = user_location.get("city_name")
    latitude = user_location.get("latitude")
    longitude = user_location.get("longitude")

    await state.update_data(
        city=city_name,
        user_latitude=latitude,
        user_longitude=longitude
    )

    await state.set_state(SetupStates.waiting_for_time)

    await msg.answer(
        f"📍 City detected: <b>{city_name}</b>.\n\n"
        f"Please enter the time you want to receive daily weather updates "
        f"in <b>HH:MM</b> format (24-hour clock, e.g., 08:00 or 22:30):",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetupStates.waiting_for_time, F.text == "❌ Cancel")
async def cancel_schedule(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Schedule setup canceled.", reply_markup=ReplyKeyboardRemove()
    )


@router.message(SetupStates.waiting_for_time, F.text)
async def process_time_input(msg: Message, state: FSMContext):
    time_str = msg.text.strip()
    tf = TimezoneFinder()

    try:
        datetime.datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await msg.answer(
            "❌ Invalid time format.\n"
            "Please enter time strictly in <b>HH:MM</b> format (e.g., 07:30, 23:15):",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    fsm_data = await state.get_data()
    city_name = fsm_data.get("city")
    latitude = fsm_data.get("user_latitude")
    longitude = fsm_data.get("user_longitude")

    await msg.answer(
        "Saving your automated schedule... ⏳",
        reply_markup=ReplyKeyboardRemove()
    )
    user_timezone = tf.timezone_at(lng=longitude, lat=latitude)

    schedule_data = await APIClient.create_schedule(
        msg.from_user.id,
        city_name,
        time_str,
        timezone=user_timezone if user_timezone else "UTC"
    )
    
    if not schedule_data:
        await msg.answer(
            "❌ Unexpected API Error occured. The schedule not created."
        )
        await state.clear()
        return

    await msg.answer(
        f"✅ <b>SkySentry Schedule Active!</b>\n\n"
        f"🗺️ Destination: <b>{city_name}</b>\n"
        f"⏰ Broadcast Time: <b>{time_str} UTC</b>\n\n"
        f"You will now automatically receive weather forecasts at this exact time everyday.",
        parse_mode="HTML"
    )

    await state.clear()