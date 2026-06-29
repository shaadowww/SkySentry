# Backend connection file
# Requests to Backend

import httpx
import logging
from bot.config import settings

logger = logging.getLogger("bot")

class APIClient:
    """Isolated class for sending requests to FastAPI backend"""

    client: httpx.AsyncClient | None = None

    @classmethod
    async def upsert_user(cls, telegram_id: int, username: str | None) -> bool:
        """Create or update a user in the database"""
        payload = {
            "telegram_id": telegram_id, 
            "username": username
        }

        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.post(
                    f"{settings.BACKEND_URL}/users/",
                    json=payload,
                    timeout=5.0
                )

                return response.status_code == 200
            
            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.post(
                    f"{settings.BACKEND_URL}/users/",
                    json=payload,
                    timeout=5.0
                )
                return response.status_code == 200
            
        except httpx.RequestError as e:
            logger.error(f"Backend connection error while upsert_user was executing: {str(e)}")
            return None
            
            
    @classmethod
    async def set_location(
        cls, 
        telegram_id: int,
        city_name: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None
    ) -> dict | None:
        """Set User Location"""

        payload = {
            "telegram_id": telegram_id,
            "city_name": city_name if city_name is not None else None,
            "latitude": latitude if latitude is not None else None,
            "longitude": longitude if longitude is not None else None,
            "city_id": None
        }

        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.post(
                    f"{settings.BACKEND_URL}/locations/",
                    json=payload,
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "not found"}
                return None
            
            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.post(
                    f"{settings.BACKEND_URL}/locations/",
                    json=payload,
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "not found"}
                return None
        except httpx.RequestError as e:
            logger.error(f"Backend connection error while set_location executing: {str(e)}")
            return None
            
    @classmethod
    async def get_location(cls, telegram_id: int) -> dict | None:
        """Get User Location"""
        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.get(
                    f"{settings.BACKEND_URL}/locations/{telegram_id}",
                    timeout=5.0
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "not found"}
                return None
        
            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.get(
                    f"{settings.BACKEND_URL}/locations/{telegram_id}",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "not found"}
                return None
            

        except httpx.RequestError as e:
            logger.error(f"Backend connection error while get_location executing: {str(e)}")
            return None

    @classmethod
    async def create_schedule(cls, telegram_id: int, city: str, time_str: str, timezone: str) -> dict | None:
        """Set User Schedule"""

        payload = {
            "telegram_id" : telegram_id,
            "city": city,
            "time": time_str,
            "timezone": timezone,
            "is_active": True
        }
        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.post(
                    f"{settings.BACKEND_URL}/schedules/",
                    json=payload,
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                return None
            
            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.post(
                    f"{settings.BACKEND_URL}/schedules/",
                    json=payload,
                    timeout=5.0
                )
            
        except httpx.RequestError as e:
            logger.error(f"Backend connection error while create_schedule executing: {str(e)}")
            return None
        
    @classmethod
    async def get_weather_now(cls, telegram_id: int) -> dict | None:
        """Get Weather Now For User"""

        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.get(
                    f"{settings.BACKEND_URL}/weather/now/{telegram_id}",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "location_not_set"}
                return None
            
            async with httpx.AsyncClient() as backup_client:
                response = await backup_client.get(
                    f"{settings.BACKEND_URL}/weather/now/{telegram_id}",
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "location_not_set"}
                return None
            
        except httpx.RequestError as e:
            logger.error(f"Backend connection error while get_weather_now executing: {str(e)}")
            return None