# APScheduler Tasks File
import datetime
import logging
import pytz
from aiogram.types import BufferedInputFile

from backend.scheduler.decorators import session_deco
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import (
    get_active_schedules, 
    get_user_location
)
from backend.services import WeatherClient

from bot.main import bot
from bot.utils.image_generator import WIG
from bot.handlers.weather import WEATHER_STATUS

logger = logging.getLogger("uvicorn.error")

@session_deco
async def check_send_weather_broadcast(session: AsyncSession):
    """
    Main Task Checks active schedules every minute
    """

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    active_schedules = await get_active_schedules(session)

    if not active_schedules:
        return
    

    for schedule in active_schedules:
        try:
            user_tz = pytz.timezone(schedule.timezone)
            time_now_user = now_utc.astimezone(user_tz)

            if schedule.time.hour != time_now_user.hour or schedule.time.minute != time_now_user.minute:
                continue
            
            logger.info(f"⏰ Schedule worked for {schedule.telegram_id} (City: {schedule.city})")

            location = await get_user_location(session, schedule.telegram_id)

            if not location:
                logger.warning(f"❌ Location for user {schedule.telegram_id} not found in database.")
                continue

            weather = await WeatherClient.get_current_weather(
                    latitude=location.latitude,
                    longitude=location.longitude
            )

            if not weather:
                fmt = "%Y-%m-%d %H:%M:%S"
                logger.warning(f"❌ [Scheduler] Skipping the user \"{schedule.telegram_id}\": The weather data is not available")
                bot.send_message(
                    chat_id=schedule.telegram_id,
                    text=f"While sending the weather forecast on your scheduled time ({time_now_user.strftime(fmt)}) error occured."
                )
                continue

            weather_report = (
                f"\n"
                f"Apparent Temperature: <b>{weather.apparent_temperature}°C</b>\n"
                f"Humidity: {weather.humidity}%\n"
                f"Wind Speed: {weather.wind_speed} m/s \n"
                f"Precipitation: <b>{weather.precipitation} mm</b>\n"
                f"Cloud Cover: <b>{weather.cloud_cover}%</b>\n"
            )

            card_buffer = WIG.generate_weather_card(
                schedule.city,
                weather.temperature,
                WEATHER_STATUS[weather.weather_code],
                "Day" if weather.is_day == 1 else "Night"
            )

            photo_file = BufferedInputFile(card_buffer.read(), filename="weather_report.png")

            response = await bot.send_photo(
                schedule.telegram_id,
                photo=photo_file,
                caption=weather_report,
                parse_mode="HTML"
            )
            
            if response is None:
                logger.warning(
                    f"🚀❌ [BROADCAST] Weather Schedule has not been sent to user {schedule.telegram_id}"
                )
                continue

            logger.info(
                    f"🚀 [BROADCAST] Weather Schedule has been sent to user {schedule.telegram_id}"
                )

        except Exception as e:
            logger.error(f"🚨 Schedule processing error #{schedule.id} for user {schedule.telegram_id}: {str(e)}")