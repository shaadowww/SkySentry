import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

class GeoCodingModel(BaseModel):
    """
    GeoCoding Schema for parsing specified city
    """
    city_id: int = Field(..., alias="id")
    city_name: str = Field(..., alias="name")
    latitude: float = Field(..., alias="latitude")
    longitude: float = Field(..., alias="longitude")
    country: str = Field(..., alias="country")


class GeoCodingClient:

    BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"

    @classmethod
    async def resolve_city(cls, city_name: str) -> GeoCodingModel:
        params = {
            "name": city_name,
            "count": 1,
            "language": "ru"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(cls.BASE_URL, params=params, timeout=3.0)
                response.raise_for_status()

            received_data = response.json()
            results = received_data.get("results")

            if not results or len(results) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"City {city_name} could not be found. Try enter the city name on english."
                )
            
            target_city_data = results[0]

            return GeoCodingModel.model_validate(target_city_data)
        except HTTPException:
            raise 
        except httpx.TimeoutException as e:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Geocoding service timed out."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected Geocoding provider error: {str(e)}"
            )
