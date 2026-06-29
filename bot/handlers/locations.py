# Locations Handler

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from backend.database import LocationRead

from bot.states import SetupStates
from bot.keyboards import share_location, cancel_keyboard
from bot.api.client import APIClient

router = Router()

@router.message(Command('set_city'))
async def start_city_setup(msg: Message, state: FSMContext):
    """Starts asking city state"""
    await state.set_state(
        SetupStates.waiting_for_city
    )

    city_setup_text = (
        "Please enter your city name (e.g., Odesa, London)\n"\
        "also you can share your location via Telegram GeoPoint sending\n"\
        "or use \'Share Location\' button"
    )

    await msg.answer(
        text=city_setup_text,
        reply_markup=share_location()
    )

@router.message(SetupStates.waiting_for_city, F.location)
async def process_location(msg: Message, state: FSMContext):
    """Receives user coordinates (`latitude, longitude`), sends requests to backend and processes results"""

    lat = msg.location.latitude
    lon = msg.location.longitude
    user_id = msg.from_user.id
    user_name = msg.from_user.username

    user_created = await APIClient.upsert_user(user_id, user_name)

    if not user_created:
        await msg.answer(
            "🚨 SkySentry API Error. Cannot register user. Try again later."
        )
        await state.clear()
        return
    
    location = await APIClient.set_location(user_id, latitude=lat, longitude=lon)
    
    if not location:
        await msg.answer(
            "🚨 Backend server connection error. Try again later."
        )
        await state.clear()
        return

    if location.get("error") == "not found":
        await msg.answer(
            f"❌ City by <b>latitude: {lat}</b> | <b>longitude: {lon}</b> was not found.\n" \
            "Please check the spelling and try again:",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )

        return
    
    city_name = location.get("city_name")

    await msg.answer(
        f"✅ Success! Your location is securely set to: <b>{city_name}</b>.\n",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

    await state.clear()


@router.message(SetupStates.waiting_for_city, F.text == "❌ Cancel")
async def cancel_city_setup(msg: Message, state: FSMContext):
    """State cancel"""
    await state.clear()
    await msg.answer(
        "City configuration canceled.", 
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(SetupStates.waiting_for_city, F.text)
async def process_city_name(msg: Message, state: FSMContext):
    """Receives city names, sends requests to backend and processes results"""

    city_name = msg.text.strip()

    await msg.answer(
        "Processing city data with SkySentry API...", reply_markup=ReplyKeyboardRemove()
    )

    user_id = msg.from_user.id
    user_name = msg.from_user.username

    user_created = await APIClient.upsert_user(user_id, user_name)
    if not user_created:
        await msg.answer(
            "🚨 SkySentry API Error. Cannot register user. Try again later."
        )
        await state.clear()
        return
    
    geo_data = await APIClient.set_location(user_id, city_name)

    if not geo_data:
        await msg.answer(
            "🚨 Backend server connection error. Try again later."
        )

        await state.clear()
        return
    
    if geo_data.get("error") == "not found":
        await msg.answer(
            f"❌ City <b>{city_name}</b> was not found.\n"
            "Please check the spelling and try again:",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )

        return
    
    resolved_name = geo_data.get("city_name", city_name)

    await msg.answer(
        f"✅ Success! Your location is securely set to: <b>{resolved_name}</b>.\n",
        parse_mode="HTML"
    )

    await state.clear()