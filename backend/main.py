from fastapi import FastAPI, Depends, HTTPException, status

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.db_engines import sessionmaker
from backend.database.core import (
    get_user, 
    upsert_user, 
    get_user_location, 
    set_user_location, 
    create_schedule, 
    get_all_user_schedules, 
    get_active_schedules, 
    specified_location_users
)

from backend.database.schemas import (
    UserCreate, UserRead, 
    ScheduleCreate, ScheduleRead, 
    LocationCreate, LocationRead
)

from typing import AsyncGenerator

app = FastAPI(
    title="SkySentry API",
    description="Core Backend SkySentry",
    version="1.0.0"
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    '''
    Database session Generator
    '''
    async with sessionmaker() as session:
        yield session

@app.get('/healthcheck', tags=["System"])
async def healthcheck(session: AsyncSession = Depends(get_session)):
    '''
    Healthcheck Database Endpoint
    '''
    try:
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@app.get('/health/weatherapi/ready', tags=["System"])
async def api_ready():
    '''
    Weather API Healthcheck
    '''
    try:
        pass # Weather API request
        return {"status": "healthy"}
    except Exception:
        return {"status": "degraded"}

# Users Endpoints

@app.get("/api/v1/users/{telegram_id}", response_model=UserRead, tags=["Users"])
async def get_user_endpoint(
    telegram_id: int, 
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Get User From A Database
    '''

    user = await get_user(session, telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

@app.post("/api/v1/users", response_model=UserRead, tags=["Users"])
async def upsert_user_endpoint(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Create or update a user in the database
    '''
    user = await upsert_user(session, user_data)
    return user



# Locations Endpoints 

@app.post('/api/v1/locations', response_model=LocationRead, tags=["Locations"])
async def set_location(
    loc_schema: LocationCreate,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Set User Location
    '''

    user_location = await set_user_location(session, loc_schema)
    return user_location

@app.get('/api/v1/locations/{telegram_id}', response_model=LocationRead, tags=["Locations"])
async def get_location(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Get User Location
    '''
    user_location = await get_user_location(session, telegram_id)

    if not user_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return user_location



# Schedules Endpoints

@app.post('/api/v1/schedules', response_model=ScheduleRead, tags=["Schedules"])
async def set_user_schedule(
    schedule_schema: ScheduleCreate,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Set User Schedule
    '''
    user_schedule = await create_schedule(session, schedule_schema)
    return user_schedule

@app.get('/api/v1/schedules/user/{telegram_id}', response_model=list[ScheduleRead], tags=["Schedules"])
async def get_user_schedule(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Get All User Schedules
    '''

    user_schedule = await get_all_user_schedules(session, telegram_id)
    return user_schedule

@app.get('/api/v1/schedules/active', response_model=list[ScheduleRead], tags=["Schedules"])
async def active_schedules(session: AsyncSession = Depends(get_session)):
    '''
    Get All Active Schedules
    '''

    schedules = await get_active_schedules(session)
    return schedules

# Specified City Users

@app.get('/api/v1/locations/users/city/{city_name}', response_model=list[LocationRead], tags=["Locations"])
async def get_users_from_specified_city(
    city_name: str,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Get Users From A Specified City
    '''

    users = await specified_location_users(session, city_name)
    return users