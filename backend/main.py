# Main API File

import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
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

from backend.services import (
    WeatherClient,
    CurrentWeatherResponse,
    DailyWeatherResponse,
    GeoCodingClient
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

@app.get('/healthcheck/database/ready', tags=["System"])
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
    if loc_schema.latitude is None or loc_schema.longitude is None:
        geo_data = await GeoCodingClient.resolve_city(loc_schema.city_name)
        
        loc_schema.city_id = geo_data.city_id
        loc_schema.latitude = geo_data.latitude
        loc_schema.longitude = geo_data.longitude
        loc_schema.city_name = geo_data.city_name

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

# Weather Endpoints

@app.get("/api/v1/weather/now/{telegram_id}", response_model=CurrentWeatherResponse, tags=["Weather"])
async def get_weather_now(
    telegram_id: int,
    session: AsyncSession = Depends(get_session)
    ):
    '''
    Get Weather Now For User
    '''

    location = await get_user_location(session, telegram_id)

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User location not set. Please set your city first."
        )
    
    weather_data = await WeatherClient.get_current_weather(
        latitude=location.latitude,
        longitude=location.longitude
    )
    return weather_data
    
@app.get("/api/v1/weather/forecast/{telegram_id}", response_model=DailyWeatherResponse, tags=["Weather"])
async def get_weather_forecast(
    telegram_id: int,
    date: datetime.date = Query(..., description="(YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
    ):
    location = await get_user_location(session, telegram_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User location not set. Please set your city first."
        )
    
    forecast_data = await WeatherClient.get_weather_for_date(
        latitude=location.latitude,
        longitude=location.longitude,
        target_date=date
    )

    return forecast_data