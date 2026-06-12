# Locations API Route File

from fastapi import APIRouter, Depends, HTTPException
from backend.database import (
    LocationRead, LocationCreate

)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services import GeoCodingClient
from backend.database import (
    set_user_location, 
    get_user_location, 
    specified_location_users,
    provide_session
)

router = APIRouter(
    prefix="/api/v1/locations",
    tags=["Locations"]
)

@router.post('/', response_model=LocationRead)
async def set_location(
    loc_schema: LocationCreate,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Set User Location
    """
    if loc_schema.latitude is None or loc_schema.longitude is None:
        geo_data = await GeoCodingClient.resolve_city(loc_schema.city_name)
        
        loc_schema.city_id = geo_data.city_id
        loc_schema.latitude = geo_data.latitude
        loc_schema.longitude = geo_data.longitude
        loc_schema.city_name = geo_data.city_name

    user_location = await set_user_location(session, loc_schema)
    return user_location

@router.get('/{telegram_id}', response_model=LocationRead)
async def get_location(
    telegram_id: int,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Get User Location
    """
    user_location = await get_user_location(session, telegram_id)

    if not user_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return user_location

@router.get('/users/city/{city_name}', response_model=list[LocationRead])
async def get_users_from_specified_city(
    city_name: str,
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Get Users From A Specified City
    """

    users = await specified_location_users(session, city_name)
    return users