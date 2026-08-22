from datetime import datetime, timezone

from pydantic import BaseModel, model_validator


class RoomBookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("Time doesn't match")
        return self

    @model_validator(mode="after")
    def check_not_in_past(self):
        if self.start_time.tzinfo is None:
            raise ValueError("start_time must include a timezone offset")
        if self.start_time <= datetime.now(timezone.utc):
            raise ValueError("start_time must be in the future")
        return self

class RoomBookingRead(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime

    room_id: int
    user_id: int

    model_config = {"from_attributes": True}

class RoomBookingReschedule(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def check_time_order(self):
        if self.end_time <= self.start_time:
            raise ValueError("Time doesn't match")
        return self

    @model_validator(mode="after")
    def check_not_in_past(self):
        if self.start_time.tzinfo is None:
            raise ValueError("start_time must include a timezone offset")
        if self.start_time <= datetime.now(timezone.utc):
            raise ValueError("start_time must be in the future")
        return self