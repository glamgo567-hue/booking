from datetime import date as date_
from datetime import datetime

from pydantic import BaseModel


class DeskCreate(BaseModel):
    floor: int

class DeskRead(BaseModel):
    id: int 
    floor: int
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}

class DeskUpdate(BaseModel):
    floor: int | None = None
    is_active: bool | None = None

class DeskAvailability(BaseModel):
    date: date_
    available: int