import datetime

import httpx

from pydantic import BaseModel, Field, JsonValue

from fastapi import HTTPException, status


class CurrentWeatherResponse(BaseModel):
    """Weather Schema for validating weather data"""

    temperature: float = Field(..., alias="temperature_2m")
    apparent_temperature: float = Field(..., alias="apparent_temperature")
    humidity: int = Field(..., alias="relative_humidity_2m")
    wind_speed: float = Field(..., alias="wind_speed_10m")
    weather_code: int = Field(..., alias="weather_code")
    precipitation: float = Field(..., alias="precipitation")
    cloud_cover: int = Field(..., alias="cloud_cover")
    is_day: int = Field(..., alias="is_day")

class DailyWeatherResponse(BaseModel):
    """
    Weather Schema for validating weather data for a date
    """
    
    date: datetime.date = Field(..., alias="time")
    max_temperature: float = Field(..., alias="temperature_2m_max")
    min_temperature: float = Field(..., alias="temperature_2m_min")
    min_apparent_temperature: float = Field(..., alias="apparent_temperature_min")
    max_apparent_temperature: float = Field(..., alias="apparent_temperature_max")
    max_wind_speed: float = Field(..., alias="wind_speed_10m_max")
    min_wind_speed: float = Field(..., alias="wind_speed_10m_min")
    precipitation_sum: float = Field(..., alias="precipitation_sum")
    weather_code: int = Field(..., alias="weather_code")
    
    



class WeatherClient:
    """Open Meteo API Class"""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    client: httpx.AsyncClient | None = None

    @classmethod
    async def _send_request(cls, url: str, *, params: dict, timeout: float = 5.0) -> JsonValue:
        """
        Send the request asynchronous
        """

        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                return response.json()

            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.get(url, params=params, timeout=timeout)
                response.raise_for_status()
            data = response.json()
            return data
        
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Weather service response timeout."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Weather service returned bad status: {e.response.status_code}"
            )

    @classmethod
    async def get_current_weather(cls, latitude: float, longitude: float) -> CurrentWeatherResponse:
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "relative_humidity_2m,"
                "weather_code,"
                "wind_speed_10m,"
                "precipitation,"
                "cloud_cover,"
                "is_day"
            ),
            "wind_speed_unit": "ms",
            "timezone": "auto"
        }

        try:
            res = await cls._send_request(cls.BASE_URL, params=params)
            needed_data = res.get("current")

            if not needed_data:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Incomplete data received from weather provider."
                )
            
            return CurrentWeatherResponse.model_validate(needed_data)
        
        except HTTPException:
            raise
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error in weather service : {str(e)}"
            )

    
    @classmethod
    async def get_weather_for_date(cls, latitude: float, longitude: float, target_date: datetime.date) -> DailyWeatherResponse:
        date_str = target_date.strftime("%Y-%m-%d")
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "apparent_temperature_max,"
                "apparent_temperature_min,"
                "wind_speed_10m_max,"
                "wind_speed_10m_min,"
                "precipitation_sum,"
                "weather_code"
            ),
            "timezone": "auto"
        }
        try:
            res = await cls._send_request(cls.BASE_URL, params=params)
            needed_data = res.get("daily")

            if not needed_data:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Invalid daily structure from weather provider."
                )
            
            cleaned_data: dict[str, (int, float, datetime.time)] = {
                "time": needed_data["time"][0],
                "temperature_2m_max": needed_data["temperature_2m_max"][0],
                "temperature_2m_min": needed_data["temperature_2m_min"][0],
                "apparent_temperature_max": needed_data["apparent_temperature_max"][0],
                "apparent_temperature_min": needed_data["apparent_temperature_min"][0],
                "wind_speed_10m_max": needed_data["wind_speed_10m_max"][0],
                "wind_speed_10m_min": needed_data["wind_speed_10m_min"][0],
                "precipitation_sum": needed_data["precipitation_sum"][0],
                "weather_code": needed_data["weather_code"][0]
            }
            
            return DailyWeatherResponse.model_validate(cleaned_data)
        
        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected weather service error: {str(e)}"
            )
