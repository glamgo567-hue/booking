from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import Base


class Desk(Base):
    __tablename__ = "desks"
    id: Mapped[int] = mapped_column(primary_key=True)
    floor: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
