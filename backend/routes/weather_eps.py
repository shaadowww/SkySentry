# Weather API Route File

import datetime
from fastapi import (
    APIRouter, 
    status, 
    HTTPException, 
    Depends, 
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services import (
    WeatherClient, 
    GeoCodingClient,
    CurrentWeatherResponse, 
    DailyWeatherResponse,
)
from backend.database import (
    get_user_location, 
    provide_session,
)
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/weather",
    tags=["Weather"]
)

class CityWeatherResponse(BaseModel):
    city_name: str
    weather: CurrentWeatherResponse


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

@router.get("/city/now", response_model=CityWeatherResponse, response_model_by_alias=False)
async def get_weather_now_by_city(
    city_name: str | None = Query(None, description="City name"),
    latitude: float | None = Query(None, description="Latitude"),
    longitude: float | None = Query(None, description="Longitude"),
):
    """Receive the weather information in specified city or coordinates"""

    if city_name is None and (latitude is None or longitude is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'city_name' or both 'latitude' and 'longitude' must be provided."
        )

    if city_name is not None:
        geo_data = await GeoCodingClient.resolve_city(city_name)
        if geo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        latitude = geo_data.latitude
        longitude = geo_data.longitude
    else:
        city_name = await GeoCodingClient.resolve_coordinates(
            latitude=latitude,
            longitude=longitude,
        )
    
    weather_data = await WeatherClient.get_current_weather(
        latitude=latitude,
        longitude=longitude,
    )

    if not weather_data or weather_data.temperature is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather data unavailable for specified location"
        )

    return {
        "city_name": city_name,
        "weather": weather_data
    }
    
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

@router.get("/forecast/range/{telegram_id}")
async def get_weather_forecast_range(
    telegram_id: int,
    days: int = Query(7, ge=1, le=16, description="Number of days (1 to 16)"),
    session: AsyncSession = Depends(provide_session)
):
    """Receive daily forecast for specified number of days"""

    location = await get_user_location(
        session, 
        telegram_id
    )

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User location not set. Please set your city first."
        )

    forecast_data = await WeatherClient.get_daily_forecast_range(
        latitude=location.latitude,
        longitude=location.longitude,
        days=days
    )

    return {
        "city_name": location.city_name,
        "forecast": forecast_data
    }