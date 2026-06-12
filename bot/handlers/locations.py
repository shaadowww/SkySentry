# bot locations handlers

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.states.user_states import SetupStates
from bot.keyboards.reply import get_cancel_keyboard
from bot.api.client import APIClient

router = Router()

@router.message(Command('set_city'))
async def start_city_setup(msg: Message, state: FSMContext):
    """Starts asking city state"""
    await state.set_state(
        SetupStates.waiting_for_city
    )

    await msg.answer(
        "Please enter your city name (e.g., Odesa, London):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(SetupStates.waiting_for_city, F.text == "❌ Cancel")
async def cancel_city_setup(msg: Message, state: FSMContext):
    """State cancel"""
    await state.clear()
    await msg.answer(
        "City configuration canceled.", reply_markup=ReplyKeyboardRemove()
    )

@router.message(SetupStates.waiting_for_city, F.text)
async def process_city_input(msg: Message, state: FSMContext):
    """Receives text, sends requests to backend and processes results"""

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
    
    if geo_data.get("error") == "not_found":
        await msg.answer(
            f"❌ City <b>{city_name}</b> was not found.\n"
            "Please check the spelling and try again:",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

        return
    
    resolved_name = geo_data.get("city_name", city_name)

    await msg.answer(
        f"✅ Success! Your location is securely set to: <b>{resolved_name}</b>.\n"
        f"Now you can build your automated weather schedules via /set_schedule.",
        parse_mode="HTML"
    )

    await state.clear()