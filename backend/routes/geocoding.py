from fastapi import (
    APIRouter, 
    HTTPException, 
    status,
    Query
)

from backend.services import GeoCodingClient
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/v1/geocoding",
    tags=["Geocoding"]
)

class GeoResolveCoordinates(BaseModel):
    city_name: str
    latitude: float
    longitude: float


@router.get("/resolve", response_model=GeoResolveCoordinates)
async def resolve_city_or_coordinates(
    city_name: str | None = Query(None, description="City name to resolve"), 
    latitude: float | None = Query(None, description="Latitude"),
    longitude: float | None = Query(None, description="Longitude"),
):
    """Resolve city name to coordinates or reverse-resolve coordinates to city name"""

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

        return {
            "city_name": geo_data.city_name,
            "latitude": geo_data.latitude,
            "longitude": geo_data.longitude,
        }

    resolved_city: str = await GeoCodingClient.resolve_coordinates(latitude, longitude)
    if resolved_city is None:
        resolved_city = "Selected Location"

    return {
        "city_name": resolved_city,
        "latitude": latitude,
        "longitude": longitude,
    }