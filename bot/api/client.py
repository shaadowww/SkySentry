# Backend connection file

import httpx
import logging
from bot.config import settings

logger = logging.getLogger("bot")

class APIClient:
    """Isolated class for sending requests to FastAPI backend"""

    @classmethod
    async def upsert_user(cls, telegram_id: int, username: str | None) -> bool:
        """
        Send request to the backend, and 
        """

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.BACKEND_URL}/users/",
                    json={"telegram_id": telegram_id, "username": username},
                    timeout=5.0
                )
                return response.status_code == 200
            except httpx.RequestError as e:
                logger.error(f"Backend connection error while upsert_user was executing: {str(e)}")
                return False
            
    @classmethod
    async def set_location(cls, telegram_id: int, city_name: str) -> dict | None:
        """
        Set up city location 
        """

        payload = {
            "telegram_id": telegram_id,
            "city_name": city_name,
            "latitude": None,
            "longitude": None,
            "city_id": None
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.BACKEND_URL}/locations",
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
