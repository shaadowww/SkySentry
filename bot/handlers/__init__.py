from aiogram import Router
from .commands import router as commands_router
from .locations import router as locations_router
from .schedules import router as schedules_router
from .weather import router as weather_router

router = Router()

router.include_router(commands_router)
router.include_router(locations_router)
router.include_router(schedules_router)
router.include_router(weather_router)