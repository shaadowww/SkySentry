# Bot Weather Handler

from aiogram import Router
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram.types import Message

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
"""Define it is day or night"""

@router.message(Command("now"))
async def check_weather_now(msg: Message):
    """Request for weather now"""
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
        f"\n"
        f"Apparent Temperature: <b>{apparent}°C</b>\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind} m/s \n"
        f"Precipitation: <b>{precipitation} mm</b>\n"
        f"Cloud Cover: <b>{cloud_cover}%</b>\n"
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