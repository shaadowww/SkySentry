# Database Tables

from sqlalchemy import ForeignKey, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column
from database.db_engines import Base
from datetime import datetime, time
from typing import Annotated

userid_fk = Annotated[int, mapped_column(ForeignKey("users.telegram_id"))]
int_pk = Annotated[int, mapped_column(primary_key=True)]



class Users(Base):
    """
    ### General users table to know your users
    """
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE ('utc', now())")
    )


class Schedules(Base):
    """
    ### Table for storing data about weather newsletter
    """
    __tablename__ = "schedules"

    id: Mapped[int_pk]
    user_id: Mapped[userid_fk]
    city: Mapped[str]
    time: Mapped[time]
    timezone: Mapped[str] = mapped_column(
        default="UTC"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )

class Locations(Base):
    """
    ### Avoid having to manually enter a city for each weather request.
    """
    __tablename__ = "locations"
    
    id: Mapped[int_pk]
    user_id: Mapped[userid_fk]
    city_name: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]