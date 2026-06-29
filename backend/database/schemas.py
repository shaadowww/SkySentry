# Schemas For Data Validation before adding to database

from pydantic import BaseModel, Field, ConfigDict
import datetime

# ` USERS `

class UserBase(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=32)

class UserCreate(UserBase):    
    telegram_id: int 

class UserRead(UserBase):
    telegram_id: int
    created_at: datetime.datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(UserBase):
    pass

# ` Schedules `

class ScheduleBase(BaseModel):
    telegram_id: int
    city: str
    time: datetime.time
    timezone: str = "UTC"
    

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleRead(ScheduleBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class ScheduleUpdate(BaseModel):
    city: str | None = None
    time: datetime.time | None = None
    timezone: str | None = None
    is_active: bool | None = None

# ` Locations `

class LocationBase(BaseModel):
    city_name: str | None = Field(None)
    
class LocationCreate(LocationBase):
    telegram_id: int
    city_id: int | None = Field(None, alias="id")
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)

class LocationRead(LocationBase):
    id: int
    telegram_id: int
    city_id: int
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)