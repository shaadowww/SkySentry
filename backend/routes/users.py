# Users API Route File
from fastapi import APIRouter, status,  HTTPException, Depends
from backend.database import (
    get_user,  upsert_user,
    UserRead, UserCreate
)
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import provide_session

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


@router.get("/{telegram_id}", response_model=UserRead)
async def get_user_endpoint(
    telegram_id: int, 
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Get User From A Database
    """

    user = await get_user(session, telegram_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    return user

@router.post("/", response_model=UserRead)
async def upsert_user_endpoint(
    user_data: UserCreate, 
    session: AsyncSession = Depends(provide_session)
    ):
    """
    Create or update a user in the database
    """
    user = await upsert_user(session, user_data)
    return user