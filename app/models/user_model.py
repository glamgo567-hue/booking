import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base

if TYPE_CHECKING:
    from app.models.desk_booking_model import DeskBooking
    from app.models.room_booking_model import RoomBooking

class UserRole(enum.Enum):
    USER = "user"
    OFFICE_MANAGER = "office_manager"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    room_bookings: Mapped[list["RoomBooking"]] = relationship(back_populates="user")
    desk_bookings: Mapped[list["DeskBooking"]] = relationship(back_populates="user")    