# Bot Weather Handler
import datetime
from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.fsm.context import FSMContext

from bot.api.client import APIClient
from bot.utils.image_generator import WIG


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