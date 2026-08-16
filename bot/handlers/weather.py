# Bot Weather Handler
import datetime
from aiogram import Router, F
from aiogram.types import (
    BufferedInputFile, 
    CallbackQuery, 
    ReplyKeyboardRemove,
    InputMediaPhoto,
)
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.fsm.context import FSMContext

from bot.api.client import APIClient
from bot.utils.image_generator import WIG
from bot.keyboards import share_location
from bot.keyboards.forecast_kb import (
    RangeSelectCallback,
    PageNavCallback,
    get_range_selection_keyboard,
    get_forecast_navigation_keyboard,
)
from bot.states import *

from io import BytesIO


router = Router()

WEATHER_STATUS = {
    0: "Clear sky ☀️",
    1: "Mainly clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    48: "Depositing Rime Fog 🌫️",
    51: "Light Drizzle 🌧️",
    53: "Moderate Drizzle 🌧️",
    55: "Dense Drizzle 🌧️",
    56: "Light Freezing Drizzle 🌨️",
    57: "Dense Freezing Drizzle 🌨️",
    61: "Little rain 🌧️",
    63: "Moderate Rain 🌧️",
    65: "Heavy Rain ⛈️",
    66: "Light Freezing Rain 🌨️",
    67: "Dense Freezing Rain 🌨️",
    71: "Snow Flurry 🌨️",
    73: "Snowfall 🌨️",
    75: "Heavy Snowfall ❄️",
    77: "Snow Grains ❄️",
    80: "Slight Rain Shower 🌧️",
    81: "Moderate Rain Shower 🌧️",
    82: "Violent Rain Shower 🌧️",
    85: "Slight Snow Shower ❄️",
    86: "Heavy Snow Shower ❄️",
    95: "Storm ⛈️"
} 
"""Weather Codes"""


daylight = {
    0: "Night",
    1: "Day"
}
"""Defining it is day or night"""

def _generate_day_card_and_caption(city_name: str, day_data: dict) -> tuple[BytesIO, str]:
    """Generate a day card and output caption for user"""

    date_obj = datetime.date.fromisoformat(day_data["date"])
    formatted_date = date_obj.strftime("%A, %d, %B")

    min_temp = day_data["min_temp"]
    max_temp = day_data["max_temp"]
    min_app = day_data.get("min_apparent", min_temp)
    max_app = day_data.get("max_apparent", max_temp)
    wind = day_data["wind_speed"]
    precipitation = day_data["precipitation"]
    weather_code = day_data["weather_code"]

    weather_desc = WEATHER_STATUS.get(weather_code, "Cloudy ☁️")
    cleared_state = weather_desc.rsplit(" ", 1)[0]

    caption = (
        f"📍 <b>{city_name.capitalize()}</b> | 📅 <b>{formatted_date}</b>\n\n"
        f"🌥️ Weather: <b>{weather_desc}</b>\n"
        f"🌡️ Temperature: <code>{min_temp}°C ... {max_temp}°C</code>\n"
        f"🌡️ Feels like: <code>{min_app}°C ... {max_app}°C</code>\n"
        f"🍃 Max wind speed: <code>{wind} м/с</code>\n"
        f"💦 Precipitation: <b>{precipitation} мм</b>\n"
    )

    card_buffer = WIG.generate_daily_weather_card(
        city=city_name.capitalize(),
        date_text=formatted_date,
        min_temp=min_temp,
        max_temp=max_temp,
        weather_state=cleared_state
    )

    return card_buffer, caption

@router.message(Command("now"))
async def check_weather_now(msg: Message):
    """Receive the weather now"""

    assert msg.from_user is not None
    
    telegram_id = msg.from_user.id
    location = await APIClient.get_location(telegram_id)

    if not location or "error" in location:
        await msg.answer(
            "⚠️ You have not specified your city!\n"
            "Use the command <b>/set_city</b>.",
            parse_mode="HTML"
        )
        return
    
    user_location = location.get("city_name", "Unknown City")


    weather_data = await APIClient.get_weather_now(telegram_id)

    if not weather_data:
        await msg.answer("🚨 Could not obtain weather data.")
        return

    if weather_data.get("error") == "location_not_set":
        await msg.answer(
            "⚠️ You have not specified your city!\n"
            "Use the command <b>/set_city</b>.",
            parse_mode="HTML"
        )
        return

    temp = weather_data.get("temperature")
    apparent = weather_data.get("apparent_temperature")
    humidity = weather_data.get("humidity")
    wind = weather_data.get("wind_speed")
    weather_code = weather_data.get("weather_code", 0)
    precipitation = weather_data.get("precipitation")
    cloud_cover = weather_data.get("cloud_cover")
    is_day = weather_data.get("is_day")

    state = WEATHER_STATUS.get(weather_code, "Data about precipitation is unavailable.")
    day_or_night = daylight.get(is_day, "Data about daylight is unavailable.")

    cleared_state = state.rsplit(" ", 1)[0]
    weather_report = (
        f"\n\n"
        f"🌡️ Apparent Temperature: <b>{apparent}°C</b>\n"
        f"🫧 Humidity: {humidity}%\n"
        f"🍃 Wind Speed: {wind} m/s \n"
        f"💦 Precipitation: <b>{precipitation} mm</b>\n"
        f"☁️ Cloud Cover: <b>{cloud_cover}%</b>\n"
    )


    card_buffer = WIG.generate_weather_card(
        city=user_location,
        temp=temp,
        weather_state=cleared_state,
        day_state=day_or_night
    )

    photo_file = BufferedInputFile(card_buffer.read(), filename="weather_report.png")
    
    await msg.answer_photo(
        photo=photo_file,
        caption=weather_report,
        parse_mode="HTML"
    )

@router.message(Command("daily"))
async def daily_weather_forecast(msg: Message, state: FSMContext):
    """Receive Daily Weather Forecast"""

    assert msg.from_user is not None

    telegram_id = msg.from_user.id
    location = await APIClient.get_location(telegram_id)

    if not location or "error" in location:
        await msg.answer(
            "⚠️ You have not specified your city!\n"
            "Use the command <b>/set_city</b>.",
            parse_mode="HTML"
        )
        return
    
    ulocation: str = location.get("city_name", "Unknown city")

    calendar_markup = await SimpleCalendar().start_calendar()
    await state.update_data(
        user_location=ulocation
    )

    await msg.answer(
        f"📍 City: <b>{ulocation}</b>\n"
        f"Please select a date for the weather forecast:",
        reply_markup=calendar_markup,
        parse_mode="HTML"
    )

@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    if "CANCEL" in callback_data.act:
        await callback.answer()
        await callback.message.edit_text("❌ Daily weather forecast cancelled.")
        await state.clear()
        return

    calendar = SimpleCalendar(show_alerts=True)
    selected, date_obj = await calendar.process_selection(callback, callback_data)
    fsm_data = await state.get_data()
    user_city = fsm_data.get("user_location")

    if not selected:
        return
    
    selected_date = date_obj.date()
    today = datetime.date.today()

    if selected_date <= today:
        await callback.answer(
            "⚠️ You can only select future dates (starting from tomorrow)!",
            show_alert=True
        )
        await callback.message.edit_text("❌ Daily weather forecast cancelled.")
        await state.clear()
        return
    
    await callback.answer()

    date_str = selected_date.isoformat()

    await callback.message.edit_text(
        f"Searching for weather forecast for <b>{selected_date.strftime('%d %B')}</b>... ⏳", 
        parse_mode="HTML"
    )

    forecast_data: dict | None = await APIClient.daily_weather_forecast(
        telegram_id=callback.from_user.id,
        date_str=date_str
    )

    if not forecast_data or "error" in str(forecast_data):
        await callback.message.edit_text(
            "❌ Could not load forecast for this day. Please try again."
        )
        return

    formatted_date = selected_date.strftime('%A, %d %B')

    max_temperature: float = forecast_data.get("max_temperature")
    min_temperature: float = forecast_data.get("min_temperature")
    min_apparent_temperature: float = forecast_data.get("min_apparent_temperature")
    max_apparent_temperature: float = forecast_data.get("max_apparent_temperature")
    max_wind_speed: float = forecast_data.get("max_wind_speed")
    min_wind_speed: float = forecast_data.get("min_wind_speed")
    precipitation_sum: float = forecast_data.get("precipitation_sum")
    weather: int = forecast_data.get("weather_code")

    cleared_weather = WEATHER_STATUS.get(weather)

    weather_answer = (
        "\n\n"
        f"🌡️ Min Apperent Temperature: <code>{min_apparent_temperature}°C</code>\n"
        f"🌡️ Max Apperent Temperature: <code>{max_apparent_temperature}°C</code>\n"
        f"🍃 Min Wind Speed: <code>{min_wind_speed} m/s</code>\n"
        f"🍃 Max Wind Speed: <code>{max_wind_speed} m/s</code>\n"
        f"💦 Precipitation: <code>{precipitation_sum} mm</code>\n"
        f"🌥️ Weather: <b>{cleared_weather}</b>\n"
    )

    card_buffer = WIG.generate_daily_weather_card(
        city=user_city,
        date_text=formatted_date,
        min_temp=min_temperature,
        max_temp=max_temperature,
        weather_state=cleared_weather.rsplit(" ", 1)[0]
    )

    photo_file = BufferedInputFile(card_buffer.read(), filename="weather_daily_forecast.png")

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=photo_file,
        caption=weather_answer,
        parse_mode="HTML"
    )

    await state.clear()

@router.message(Command('city_weather'))
async def weather_city_now(msg: Message, state: FSMContext): 
    waiting_city_name_text = (
        "⌨️ Please enter your city name <b>(e.g., Odesa, London)</b>\n"\
        "<i>🌍 Also you can share your location via <b>Telegram GeoPoint</b> sending</i>\n"
    )
    await state.set_state(SetupStates.weather_by_city)

    await msg.answer(
        waiting_city_name_text,
        parse_mode="HTML",
        reply_markup=share_location()
    )

@router.message(SetupStates.weather_by_city, F.text == "❌ Cancel")
async def weather_city_request_cancel(msg: Message, state: FSMContext):
    """Cancel the weather for city request operation"""

    await state.clear()
    await msg.reply(
        "Weather for city request cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(SetupStates.weather_by_city, F.text)
async def process_weather_for_city_request(msg: Message, state: FSMContext):
    """Weather for city request by receiving text name"""
    assert msg.text is not None
    assert msg.from_user is not None

    city_name = msg.text.strip()

    await msg.answer(
        "Processing city data with SkySentry API...", 
        reply_markup=ReplyKeyboardRemove()
    )

    user_created = await APIClient.upsert_user(msg.from_user.id, msg.from_user.username)
    if not user_created:
        await msg.answer(
            "🚨 SkySentry API Error. Cannot register user. Try again later."
        )
        await state.clear()
        return

    weather_data = await APIClient.get_weather_now_by_city_or_coordinates(city_name=city_name)

    if not weather_data:
        await msg.answer("🚨 Could not obtain weather data.")
        await state.clear()
        return
    
    if weather_data.get("error") == "city_not_found":
        await msg.answer(
            f"❌ City <b>{city_name}</b> was not found.\n"
            "Please check the spelling and try again:",
            parse_mode="HTML"
        )
        return

    city_name: str = weather_data.get("city_name", "Unknown city")
    weather_info: dict = weather_data.get("weather", {})

    temp = weather_info.get("temperature")

    if temp is None:
            await msg.answer(
                f"❌ Could not obtain valid weather data for <b>{city_name}</b>. Please check the city name.",
                parse_mode="HTML"
            )
            await state.clear()
            return

    
    apparent = weather_info.get("apparent_temperature")
    humidity = weather_info.get("humidity")
    wind = weather_info.get("wind_speed")
    weather_code = weather_info.get("weather_code", 0)
    precipitation = weather_info.get("precipitation")
    cloud_cover = weather_info.get("cloud_cover")
    is_day = weather_info.get("is_day")

    weather_state = WEATHER_STATUS.get(weather_code, "Data about precipitation is unavailable.")
    day_or_night = daylight.get(is_day, "Data about daylight is unavailable.")

    cleared_state = weather_state.rsplit(" ", 1)[0]
    weather_report = (
        f"\n\n"
        f"🌡️ Apparent Temperature: <b>{apparent}°C</b>\n"
        f"🫧 Humidity: {humidity}%\n"
        f"🍃 Wind Speed: {wind} m/s \n"
        f"💦 Precipitation: <b>{precipitation} mm</b>\n"
        f"☁️ Cloud Cover: <b>{cloud_cover}%</b>\n"
    )

    card_buffer = WIG.generate_weather_card(
        city=city_name.capitalize(),
        temp=temp,
        weather_state=cleared_state,
        day_state=day_or_night
    )

    photo_file = BufferedInputFile(card_buffer.read(), filename="weather_report.png")
        
    await msg.answer_photo(
        photo=photo_file,
        caption=weather_report,
        parse_mode="HTML"
    )

    await state.clear()

@router.message(SetupStates.weather_by_city, F.location)
async def process_weather_for_city_request_by_location(msg: Message, state: FSMContext):
    """Weather for city request by receiving coordinates"""

    assert msg.location is not None
    assert msg.from_user is not None

    latitude = msg.location.latitude
    longitude = msg.location.longitude

    await msg.answer(
        "Processing city data with SkySentry API...", 
        reply_markup=ReplyKeyboardRemove()
    )

    user_created = await APIClient.upsert_user(msg.from_user.id, msg.from_user.username)
    if not user_created:
        await msg.answer(
            "🚨 SkySentry API Error. Cannot register user. Try again later."
        )
        await state.clear()
        return

    weather_data = await APIClient.get_weather_now_by_city_or_coordinates(
        latitude=latitude,
        longitude=longitude,
    )

    if not weather_data:
        await msg.answer("🚨 Could not obtain weather data.")
        await state.clear()
        return

    if weather_data.get("error") == "city_not_found":
        await msg.answer(
            f"❌ City by <b>latitude: {latitude}</b> | <b>longitude: {longitude}</b> was not found.\n" \
            "Please check the spelling and try again:",
            parse_mode="HTML"
        )
        return

    city_name: str = weather_data.get("city_name", "Unknown city")
    weather_info: dict = weather_data.get("weather", {})

    temp = weather_info.get("temperature")

    if temp is None:
        await msg.answer(
            f"❌ Could not obtain valid weather data for <b>{city_name}</b>. Please check the city name.",
            parse_mode="HTML"
        )
        await state.clear()
        return

    apparent = weather_info.get("apparent_temperature")
    humidity = weather_info.get("humidity")
    wind = weather_info.get("wind_speed")
    weather_code = weather_info.get("weather_code", 0)
    precipitation = weather_info.get("precipitation")
    cloud_cover = weather_info.get("cloud_cover")
    is_day = weather_info.get("is_day")

    weather_state = WEATHER_STATUS.get(weather_code, "Data about precipitation is unavailable.")
    day_or_night = daylight.get(is_day, "Data about daylight is unavailable.")

    cleared_state = weather_state.rsplit(" ", 1)[0]
    weather_report = (
        f"\n\n"
        f"🌡️ Apparent Temperature: <b>{apparent}°C</b>\n"
        f"🫧 Humidity: {humidity}%\n"
        f"🍃 Wind Speed: {wind} m/s \n"
        f"💦 Precipitation: <b>{precipitation} mm</b>\n"
        f"☁️ Cloud Cover: <b>{cloud_cover}%</b>\n"
    )

    card_buffer = WIG.generate_weather_card(
        city=city_name.capitalize(),
        temp=temp,
        weather_state=cleared_state,
        day_state=day_or_night
    )

    photo_file = BufferedInputFile(card_buffer.read(), filename="weather_report.png")
        
    await msg.answer_photo(
        photo=photo_file,
        caption=weather_report,
        parse_mode="HTML"
    )

    await state.clear()

@router.message(Command("forecast_range"))
async def start_forecast_range(msg: Message):
    """Choosing forecast range"""

    await msg.answer(
        "🌡️ <b>Weather forecast</b>\n"
        "Select the period you want to get an interactive forecast for:",
        reply_markup=get_range_selection_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(RangeSelectCallback.filter())
async def process_range_selected(callback: CallbackQuery, callback_data: RangeSelectCallback, state: FSMContext):
    await callback.answer("Meteodata is downloading... ⏳")
    
    days = callback_data.days
    data = await APIClient.get_forecast_range(telegram_id=callback.from_user.id, days=days)

    if not data or "forecast" not in data or not data["forecast"]:
        await callback.message.edit_text(
            "⚠️ Failed to get forecast. Make sure your city is set through /set_city."
        )
        return

    forecast_list = data["forecast"]
    city_name = data.get("city_name", "Unknown Location")

    await state.update_data(
        forecast_city=city_name,
        forecast_list=forecast_list,
        total_days=len(forecast_list)
    )

    start_index = 0
    card_buffer, caption = _generate_day_card_and_caption(city_name, forecast_list[start_index])
    photo_file = BufferedInputFile(card_buffer.read(), filename="forecast_0.png")

    await callback.message.delete()
    await callback.message.answer_photo(
        photo=photo_file,
        caption=caption,
        reply_markup=get_forecast_navigation_keyboard(start_index, len(forecast_list)),
        parse_mode="HTML"
    )


@router.callback_query(PageNavCallback.filter())
async def process_forecast_page_nav(callback: CallbackQuery, callback_data: PageNavCallback, state: FSMContext):
    target_index = callback_data.index
    fsm_data = await state.get_data()

    city_name = fsm_data.get("forecast_city")
    forecast_list = fsm_data.get("forecast_list")
    total_days = fsm_data.get("total_days")

    if not forecast_list or target_index >= total_days or target_index < 0:
        await callback.answer("⚠️ Forecast session has expired. Call /forecast again.", show_alert=True)
        return

    await callback.answer()

    card_buffer, caption = _generate_day_card_and_caption(city_name, forecast_list[target_index])
    photo_file = BufferedInputFile(card_buffer.read(), filename=f"forecast_{target_index}.png")

    media = InputMediaPhoto(media=photo_file, caption=caption, parse_mode="HTML")
    
    await callback.message.edit_media(
        media=media,
        reply_markup=get_forecast_navigation_keyboard(target_index, total_days)
    )

@router.callback_query(F.data == "ignore")
async def process_ignore_button(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "cancel_forecast")
async def process_cancel_forecast(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("The forecast is closed")
    await callback.message.delete()