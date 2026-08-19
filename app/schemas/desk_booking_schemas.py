from datetime import date as date_
from datetime import datetime

from pydantic import BaseModel


class DeskBookingCreate(BaseModel):
    date: date_

class DeskBookingRead(BaseModel):
    id: int
    date: date_
    status: str
    created_at: datetime

    user_id: int

    model_config = {"from_attributes": True}