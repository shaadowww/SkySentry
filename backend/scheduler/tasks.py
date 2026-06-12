# APScheduler Tasks File
import datetime
import logging
import pytz
from backend.scheduler.decorators import session_deco
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import (
    get_active_schedules, 
    get_user_location
)
from backend.services import WeatherClient

logger = logging.getLogger("uvicorn.error")

@session_deco
async def check_send_weather_broadcast(session: AsyncSession):
    """
    Main Task Checks active schedules every minute
    """

    active_schedules = await get_active_schedules(session)

    if not active_schedules:
        return
    
    now_utc = datetime.datetime.now(datetime.timezone.utc)

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

            logger.info(
                f"🚀 [BROADCAST] Sent to user {schedule.telegram_id} | "
                f"Weather in {schedule.city}: {weather.temperature}°C, {weather.apparent_temperature}°C apparenting"
            )
        except Exception as e:
            logger.error(f"🚨 Schedule processing error #{schedule.id} for user {schedule.telegram_id}: {str(e)}")