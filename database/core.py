# Database Query Functions

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Users, Locations, Schedules
from database.schemas import UserCreate, UserRead
from typing import Optional

# ` USERS ` 

async def upsert_user(session: AsyncSession, user_schema: UserCreate) -> UserRead:
    '''
    `Creates an user or updates an existing user if they have changed their name`
    '''

    user = await session.get(Users, user_schema.telegram_id)

    if user:
        user.username = user_schema.username
    else: 
        user = Users(**user_schema.model_dump())
        session.add(user)
    
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)

async def get_user(session: AsyncSession, telegram_id: int) -> Optional[UserRead]:
    '''
    `Checks if there's a user`
    '''

    user = await session.get(Users, telegram_id)

    if user:
        return UserRead.model_validate(user)
    else:
        return None
    
# `SCHEDULES `

pass

# ` LOCATIONS `

pass