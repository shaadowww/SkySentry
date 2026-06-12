from aiogram import Router
from .commands import router as commands_router
from .locations import router as locations_router

router = Router()


router.include_router(commands_router)
router.include_router(locations_router)