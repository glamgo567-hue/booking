from datetime import date as date_
from datetime import datetime, timezone

from pydantic import BaseModel, model_validator


class DeskBookingCreate(BaseModel):
    date: date_

    @model_validator(mode="after")
    def check_not_in_past(self):
        if self.date < datetime.now(timezone.utc).date():
            raise ValueError("date must not be in the past")
        return self

class DeskBookingRead(BaseModel):
    id: int
    date: date_
    status: str
    created_at: datetime

    user_id: int

    model_config = {"from_attributes": True}