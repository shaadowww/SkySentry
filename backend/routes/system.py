# System API Route File

from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import provide_session
from backend.services import WeatherClient

router = APIRouter(
    prefix="/api/v1/system",
    tags=["System"]
)

@router.get('/healthcheck/database/ready')
async def healthcheck(session: AsyncSession = Depends(provide_session)):
    """
    Healthcheck Database Endpoint
    """
    try:
        await session.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )


@router.get('/healthcheck/weatherapi/ready')
async def api_ready():
    """
    Weather API Healthcheck
    """
    try:
        await WeatherClient.get_current_weather(latitude=0.0, longitude=0.0)
        return {"status": "healthy"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather API connection failed: {str(e)}"
        )