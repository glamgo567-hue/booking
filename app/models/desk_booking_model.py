import enum
from datetime import date as date_
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import Base

if TYPE_CHECKING:
    from app.models.user_model import User
    
class DeskStatus(enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class DeskBooking(Base):
    __tablename__ = "desk_booking"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date_] = mapped_column(Date)
    status: Mapped[DeskStatus] = mapped_column(SQLEnum(DeskStatus), default=DeskStatus.CONFIRMED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="desk_bookings")