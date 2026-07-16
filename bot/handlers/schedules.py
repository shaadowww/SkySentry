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

@router.message(Command('set_schedule'))
async def set_schedule(msg: Message, state: FSMContext):
    assert msg.from_user is not None

    user_id = msg.from_user.id 
    user_location = await APIClient.get_location(user_id)

    if user_location is None or "error" in user_location:
        await msg.answer(
            "⚠️ You have not configured your city yet!\n"
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

@router.message(Command('all_schedules'))
async def all_schedules(msg: Message, state: FSMContext):
    assert msg.from_user is not None

    userid = msg.from_user.id

    user_schedules: list[dict] | None = await APIClient.get_user_schedules(userid)

    if user_schedules is None or len(user_schedules) == 0:
        await msg.answer(
            "⚠️ You have no any schedule."
        )
        return

    output: str = "Here's your schedules:\n\n"
    schedules_list: str = ""
    user_schedule_data = {}
    for ind, schedule in enumerate(user_schedules):
        city = schedule.get("city")
        time: datetime.time = schedule.get("time")

        result = (
        f"<b>Schedule</b> #{ind + 1}\n"
        f"- City: <b>{city}</b>\n"
        f"- Time: <code>{time}</code> everyday\n\n"
    )
        time_str = time.strftime("%H:%M") if hasattr(time, "strftime") else str(time)[:5]
        user_schedule_data[f"{ind + 1}"] = {"city": city, "time": time_str}
        output += result
        schedules_list += result

    await state.update_data(
        us_schedule_data=user_schedule_data,
        all_schedules_result=schedules_list
    )
    await msg.answer(
        output, 
        parse_mode="HTML",
        reply_markup=schedule_update
    )

@router.callback_query(F.data == "add")
async def schedule_add(callback: CallbackQuery, state: FSMContext):
    """Schedule adding Callback-Query Handler"""

    await callback.answer()

    ulocation = await APIClient.get_location(callback.from_user.id)

    if ulocation is None or "error" in ulocation:
        await callback.message.answer(
            "⚠️ You haven't configured your city yet!\n"
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

    await callback.message.answer(
        f"📍 City detected: <b>{city_name}</b>.\n\n"
        f"Please enter the time you want to receive daily weather updates "
        f"in <b>HH:MM</b> format (24-hour clock, e.g., 08:00 or 22:30):",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "remove")
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
    await callback.message.answer(
        "Schedule remove cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )

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
        f"⏰ Broadcast Time: <b>{time_str} UTC</b>\n\n"
        f"You will now automatically receive weather forecasts at this exact time everyday.",
        parse_mode="HTML"
    )

    await state.clear()