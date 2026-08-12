from datetime import datetime

from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str
    capacity: int
    equipment: str | None = None

class RoomRead(BaseModel):
    id: int 
    name: str
    capacity: int
    equipment: str | None = None
    created_at: datetime
    
    model_config={"from_attributes": True}

class RoomUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    equipment: str | None = None