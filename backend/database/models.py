# Database Tables

from sqlalchemy import ForeignKey, BigInteger, text, String
from sqlalchemy.orm import Mapped, mapped_column
from backend.database.db_engines import Base
from datetime import datetime, time
from typing import Annotated

int_pk = Annotated[int, mapped_column(primary_key=True)]



class Users(Base):
    """
    ### General users table to know your users
    """
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(
        String(32)
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE ('utc', now())")
    )


class Schedules(Base):
    """
    ### Table for storing data about weather newsletter
    """
    __tablename__ = "schedules"

    id: Mapped[int_pk]
    telegram_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    city: Mapped[str]
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
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
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id"),
        unique=True
    )
    city_id: Mapped[int] = mapped_column(BigInteger)
    city_name: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]