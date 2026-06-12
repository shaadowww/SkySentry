# Schedules API Route File

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import (
    ScheduleCreate, ScheduleRead,
    create_schedule, get_all_user_schedules, get_active_schedules,
    provide_session
)

router = APIRouter(
    prefix="/api/v1/schedules",
    tags=["Schedules"]
)

@router.post('/', response_model=ScheduleRead)
async def set_user_schedule(
    schedule_schema: ScheduleCreate,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Set User Schedule
    """
    user_schedule = await create_schedule(session, schedule_schema)
    return user_schedule

@router.get('/user/{telegram_id}', response_model=list[ScheduleRead])
async def get_user_schedule(
    telegram_id: int,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Get All User Schedules
    """

    user_schedule = await get_all_user_schedules(session, telegram_id)
    return user_schedule

@router.get('/active', response_model=list[ScheduleRead])
async def active_schedules(session: AsyncSession = Depends(provide_session)):
    """
    Get All Active Schedules
    """

    schedules = await get_active_schedules(session)
    return schedules