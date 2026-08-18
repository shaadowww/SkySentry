# Main Backend API File
import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.scheduler import SchedulerManager

from backend.services import (
    WeatherClient,
    GeoCodingClient
)
from backend.routes.users import router as users_router
from backend.routes.schedules import router as schedules_router
from backend.routes.locations import router as locations_router
from backend.routes.weather_eps import router as weather_router
from backend.routes.system import router as system_router
from backend.routes.geocoding import router as geocoding_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App Life Cycle
    """
    
    http_client = httpx.AsyncClient()
    WeatherClient.client = http_client
    GeoCodingClient.client = http_client
    
    SchedulerManager.start()

    yield

    SchedulerManager.shutdown()


app = FastAPI(
    title="SkySentry API",
    description="Core Backend SkySentry",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users_router)
app.include_router(system_router)
app.include_router(schedules_router)
app.include_router(locations_router)
app.include_router(weather_router)
app.include_router(geocoding_router)