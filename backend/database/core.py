# Database Query Functions
import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import Users, Locations, Schedules
from backend.database.schemas import UserCreate, UserRead, ScheduleCreate, ScheduleRead, LocationCreate, LocationRead

# ` USERS ` 

async def upsert_user(session: AsyncSession, user_schema: UserCreate) -> UserRead:
    """Creates A User Or Updates An Existing User If They Have Changed Their Name"""

    user = await session.get(Users, user_schema.telegram_id)

    if user:
        user.username = user_schema.username
    else: 
        user = Users(**user_schema.model_dump())
        session.add(user)
    
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)

async def get_user(session: AsyncSession, telegram_id: int) -> UserRead | None:
    """
    Get A User By ID And Check Is There it
    """

    user = await session.get(Users, telegram_id)

    return UserRead.model_validate(user) if user else None
    
# `SCHEDULES `

async def create_schedule(session: AsyncSession, schedule_schema: ScheduleCreate) -> ScheduleRead | None:
    """
    Write Down A User Schedule Into Database
    """
    query = (
        select(Schedules)
        .where(
            Schedules.telegram_id == schedule_schema.telegram_id,
            Schedules.time == schedule_schema.time
        )
    )

    res = await session.execute(query)

    existing_row = res.scalar_one_or_none()

    if existing_row is not None:
        return None
    
    schedule = Schedules(**schedule_schema.model_dump())
    session.add(schedule)

    await session.commit()
    await session.refresh(schedule)
    return ScheduleRead.model_validate(schedule)

async def get_all_user_schedules(session: AsyncSession, telegram_id: int) -> list[ScheduleRead]:
    """
    Get All Schedules User Have
    """
    query = (
        select(Schedules)
        .where(Schedules.telegram_id == telegram_id)
    )

    res = await session.execute(query)

    user_schedules = res.scalars().all()

    return [ScheduleRead.model_validate(schedule) for schedule in user_schedules]



async def get_active_schedules(session: AsyncSession) -> list[ScheduleRead]:
    """
    Get All Active Schedules (Where `is_active` is `True`)
    """

    query = (
        select(Schedules)
        .where(Schedules.is_active)
    )
    
    res = await session.execute(query)

    active_schedules = res.scalars().all()

    return [ScheduleRead.model_validate(sch) for sch in active_schedules]
    
async def remove_user_schedule(
        session: AsyncSession, 
        city: str, 
        time: datetime.time, 
        telegram_id: int
    ) -> bool:
    """Removes the specified schedule from the database"""
    
    stmt = (
        delete(Schedules)
        .where(
            Schedules.city == city,
            Schedules.time == time,
            Schedules.telegram_id == telegram_id
        )
        .returning(Schedules.id)
    )

    res = await session.execute(stmt)
    deleted_schedules = res.scalars().all()

    await session.commit()

    return len(deleted_schedules) > 0

# ` LOCATIONS `

async def set_user_location(session: AsyncSession, loc_schema: LocationCreate) -> LocationRead:
    """
    Set or update user location
    """
    
    query = (
        select(Locations)
        .where(Locations.telegram_id == loc_schema.telegram_id)
    )
    res = await session.execute(query)
    location = res.scalar_one_or_none()

    if location:
        location.city_id = loc_schema.city_id
        location.city_name = loc_schema.city_name
        location.latitude = loc_schema.latitude
        location.longitude = loc_schema.longitude
    else:
        location = Locations(**loc_schema.model_dump())
        session.add(location)

    await session.commit()
    await session.refresh(location)
    return LocationRead.model_validate(location)

async def specified_location_users(session: AsyncSession, city_name: str) -> list[LocationRead]:
    """
    Get Users From A Specified City

    *It allows get user from specified city **ONLY!***
    """

    query = (
        select(Locations)
        .where(Locations.city_name == city_name)
    )
    res = await session.execute(query)
    users = res.scalars().all()
    return [LocationRead.model_validate(user) for user in users]

async def get_user_location(session: AsyncSession, telegram_id: int) -> LocationRead | None:
    """
    Get Chosen Location By User
    """

    query = (
        select(Locations)
        .where(Locations.telegram_id == telegram_id)
    )
    res = await session.execute(query)
    user_location = res.scalar_one_or_none()
    return LocationRead.model_validate(user_location) if user_location else None