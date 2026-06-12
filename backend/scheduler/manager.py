# APScheduler Manager File
import logging


from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.scheduler import check_send_weather_broadcast

logger = logging.getLogger("uvicorn.error")

class SchedulerManager:
    scheduler = AsyncIOScheduler()

    @classmethod
    def start(cls):
        """
        Starts the scheduler and registrate ticker task
        """

        if not cls.scheduler.running:
            cls.scheduler.add_job(
                check_send_weather_broadcast,
                trigger=CronTrigger(second=0),
                id="weather_broadcaster",
                replace_existing=True
            )
            
            cls.scheduler.start()
            logger.info(f"🟢 Background APScheduler has been successfully started.")

    @classmethod
    def shutdown(cls):
        """
        Stops the scheduler
        """

        if cls.scheduler.running:
            cls.scheduler.shutdown()
            logger.info(f"🔴 Background APScheduler has been successfully stopped.")
