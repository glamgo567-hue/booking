from datetime import datetime

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