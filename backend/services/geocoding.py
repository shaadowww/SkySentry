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
    REVERSE_GEOCODING_URL = "https://nominatim.openstreetmap.org/reverse"

    client: httpx.AsyncClient | None = None
    
    @classmethod
    async def resolve_city(cls, city_name: str) -> GeoCodingModel:
        """Open Meteo Geocoding API to transform the city name to coordinates"""
        
        params = {
            "name": city_name,
            "count": 1,
            "language": "en"
        }

        try:

            if cls.client and not cls.client.is_closed:
                response = await cls.client.get(cls.BASE_URL, params=params, timeout=5)
                response.raise_for_status()
                received_data = response.json()
            else:
                async with httpx.AsyncClient() as backup_client:
                    response = await backup_client.get(cls.BASE_URL, params=params, timeout=5)
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
    
    @classmethod
    async def resolve_coordinates(cls, latitude: float, longitude: float) -> str:
        """Open Street Map API To Resolve the coordinates to transform the coordinates to city name"""

        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "en"
        }

        headers = {
            "User-Agent": "SkySentryWeatherBot/1.0 (ppupkin1337@gmail.com)"
        }

        try:
            if cls.client and not cls.client.is_closed:
                response = await cls.client.get(
                    cls.REVERSE_GEOCODING_URL,
                    params=params,
                    headers=headers,
                    timeout=5
                )
                response.raise_for_status()
                received_data = response.json()
            else:
                async with httpx.AsyncClient() as backup_client:
                    response = await cls.client.get(
                    cls.REVERSE_GEOCODING_URL,
                    params=params,
                    headers=headers,
                    timeout=5
                )
                    response.raise_for_status()
                    received_data = response.json()

            if not received_data:
                raise HTTPException(
                    status=status.HTTP_404_NOT_FOUND,
                    detail=f"City by latitude: {latitude} | longitude: {longitude} has not been found. Check specified data."
                )
            
            address = received_data.get("address")

            city_name = (
                address.get("city") or
                address.get("town") or
                address.get("village") or
                address.get("hamlet") or
                address.get("suburb")
            )

            return city_name if city_name else "Unknown city"

        except HTTPException:
            raise 
        except httpx.TimeoutException as e:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="OpenStreetMap service timed out."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected OpenStreetMap provider error: {str(e)}"
            )
