# Weather API Route File

import datetime
from fastapi import (
    APIRouter, 
    status, 
    HTTPException, 
    Depends, 
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services import (
    WeatherClient, 
    CurrentWeatherResponse, 
    DailyWeatherResponse
)
from backend.database import (
    get_user_location, 
    provide_session
)

router = APIRouter(
    prefix="/api/v1/weather",
    tags=["Weather"]
)

@router.get("/now/{telegram_id}", response_model=CurrentWeatherResponse, response_model_by_alias=False)
async def get_weather_now(
    telegram_id: int,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Get Weather Now For User
    """

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
    
@router.get("/forecast/{telegram_id}", response_model=DailyWeatherResponse, response_model_by_alias=False)
async def get_weather_forecast(
    telegram_id: int,
    date: datetime.date = Query(..., description="(YYYY-MM-DD)"),
    session: AsyncSession = Depends(provide_session)
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