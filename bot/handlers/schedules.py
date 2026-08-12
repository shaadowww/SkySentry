# Schedule Handler 
import datetime
from timezonefinder import TimezoneFinder

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import SetupStates
from bot.keyboards import *
from bot.api.client import APIClient

router = Router()

async def _initiate_schedule_create(target_message: Message, state: FSMContext, user_id: int):
    """Internal helper for creating schedules"""
    ulocation = await APIClient.get_location(user_id)

    if ulocation is None or "error" in ulocation:
        await target_message.answer(
            "⚠️ You have not configured your city yet!\n"
            "Please use the <b>/set_city</b> command first before setting up a schedule",
            parse_mode="HTML"
        )
        return

    city_name = ulocation.get("city_name")
    latitude = ulocation.get("latitude")
    longitude = ulocation.get("longitude")

    await state.update_data(
        city=city_name,
        user_latitude=latitude,
        user_longitude=longitude
    )

    await state.set_state(SetupStates.waiting_for_time)

    await target_message.answer(
        f"📍 City detected: <b>{city_name}</b>.\n\n"
        f"Please enter the time you want to receive daily weather updates "
        f"in <b>HH:MM</b> format (24-hour clock, e.g., 08:00 or 22:30):",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command('set_schedule'))
async def set_schedule(msg: Message, state: FSMContext):
    """Create Schedule Handler"""
    assert msg.from_user is not None

    await _initiate_schedule_create(msg, state, msg.from_user.id)

@router.callback_query(F.data == "add_schedule")
async def schedule_add(callback: CallbackQuery, state: FSMContext):
    """Schedule adding Callback-Query Handler"""

    await callback.answer()
    await callback.message.delete()

    await _initiate_schedule_create(callback.message, state, callback.from_user.id)

@router.callback_query(F.data == "remove_schedule")
async def remove_schedule_callback(callback: CallbackQuery, state: FSMContext):
    """Schedule remove Callback-Query Handler"""
    await callback.answer()

    fsm_data = await state.get_data()
    schedules = fsm_data.get("us_schedule_data", {})
    schedules_list: str = fsm_data.get("all_schedules_result", "")

    if not schedules:
        await callback.message.answer(
            "⚠️ No schedules found in memory."
        )
        return
    
    await state.set_state(SetupStates.delete_schedule)

    indexes_list = list(schedules.keys())

    await callback.message.edit_text(
        "<i><b>Select the schedule number you want to delete</b></i>\n\n"
        f"{schedules_list}",
        reply_markup=user_schedules_buttons(indexes_list),
        parse_mode="HTML"
    )
    
@router.callback_query(SetupStates.delete_schedule, F.data.startswith("del_num_"))
async def remove_schedule(callback: CallbackQuery, state: FSMContext):
    """Schedule remove Callback-Query Handler"""
    await callback.answer()

    target_index = callback.data.split("_")[2]

    fsm_data = await state.get_data()
    schedules = fsm_data.get("us_schedule_data")

    user_schedule = schedules.get(target_index)

    if not user_schedule:
        await callback.message.answer(
            "🚨 Error: Schedule data lost. Please start over via /all_schedules."
        )
        await state.clear()
        return

    city = user_schedule.get("city")
    time = user_schedule.get("time")

    delete_request = await APIClient.remove_user_schedule(city, time, callback.from_user.id)

    if not delete_request or "error" in str(delete_request):

        await callback.message.answer(
            f"❌ The schedule #{target_index} not deleted due to backend error.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await callback.message.answer(
        "✔️ The schedule has been deleted successfully.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@router.message(SetupStates.waiting_for_time, F.text == "❌ Cancel")
async def cancel_schedule(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "Schedule setup canceled.", reply_markup=ReplyKeyboardRemove()
    )

@router.callback_query(SetupStates.delete_schedule, F.data == "schedule_delete_cancel")
async def remove_schedule_cancel(callback: CallbackQuery, state: FSMContext):
    """Remove Schedule Cancel Callback Query"""
    await callback.answer()
    await state.clear()
    await callback.message.answer("Schedule remove cancelled.")

@router.message(SetupStates.waiting_for_time, F.text)
async def process_time_input(msg: Message, state: FSMContext):
    assert msg.text is not None
    assert msg.from_user is not None

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
    
    if schedule_data is None:
        await msg.answer(
            "❌ Unexpected API Error occured. The schedule not created."
        )
        await state.clear()
        return
    
    if "error" in schedule_data:
        await msg.answer(
            "⚠️ Schedule with this time already exists. Try again."
        )
        return

    await msg.answer(
        f"✅ <b>SkySentry Schedule Active!</b>\n\n"
        f"🗺️ Destination: <b>{city_name}</b>\n"
        f"⏰ Broadcast Time: <b>{time_str} {user_timezone}</b>\n\n"
        f"You will now automatically receive weather forecasts at this exact time everyday.",
        parse_mode="HTML"
    )

    await state.clear()