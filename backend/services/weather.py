import httpx

from pydantic import BaseModel, Field

from fastapi import HTTPException, status

class WeatherResponseBase(BaseModel):
    '''
    Weather Schema for validating weather data
    '''
    pass

class WeatherClient:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @classmethod
    async def get_current_weather(cls, latitude: float, longitude: float):
        ...
    

