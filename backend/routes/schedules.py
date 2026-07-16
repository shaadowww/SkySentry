# Schedules API Route File

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import (
    ScheduleCreate, ScheduleRead,
    create_schedule, get_all_user_schedules, get_active_schedules, remove_user_schedule,
    provide_session
)

router = APIRouter(
    prefix="/api/v1/schedules",
    tags=["Schedules"]
)

@router.post('/', response_model=ScheduleRead | None)
async def set_user_schedule(
    schedule_schema: ScheduleCreate,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Set User Schedule
    """
    
    user_schedule = await create_schedule(session, schedule_schema)

    if user_schedule is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SCHEDULE ALREADY EXISTS"
        )

        
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

@router.delete('/user/{telegram_id}')
async def remove_schedule(city: str, time: datetime.time, telegram_id: int, session: AsyncSession = Depends(provide_session)) -> bool:
    """
    Remove user schedule
    """

    schedule = await remove_user_schedule(session, city, time, telegram_id)
    return schedule