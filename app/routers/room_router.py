from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_office_manager
from app.dependencies.db import get_db
from app.models.room_booking_model import RoomBooking
from app.models.room_model import Room
from app.models.user_model import User
from app.schemas.room_schemas import RoomCreate, RoomRead, RoomUpdate

room_router = APIRouter(prefix="/rooms", tags=["room"])

@room_router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(room_data: RoomCreate, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_office_manager)):
    room = (await db.execute(select(Room).where(Room.name == room_data.name))).scalar_one_or_none()
    if room is not None:
        raise HTTPException(status_code=409, detail="Name is already occupied")
    new_room = Room(name = room_data.name,
                    capacity = room_data.capacity,
                    equipment = room_data.equipment)
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room

@room_router.get("", response_model=list[RoomRead])
async def get_rooms(skip: int = Query(0, ge=0),
                    limit: int = Query(10, ge=1, le=100), 
                    db: AsyncSession = Depends(get_db)):
    rooms = (await db.execute(select(Room).order_by(Room.created_at.desc(), Room.id.desc()).offset(skip).limit(limit))).scalars().all()
    return rooms

@room_router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: int,
                   db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@room_router.patch("/{room_id}", response_model=RoomRead)
async def fix_room(room_id: int,
                   room_data: RoomUpdate, 
                   db: AsyncSession = Depends(get_db), 
                   current_user: User = Depends(require_office_manager)):
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    update_room_data = room_data.model_dump(exclude_unset=True)
    for field, value in update_room_data.items():
        setattr(room, field, value)
    await db.commit()
    await db.refresh(room)
    return room

@room_router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_office_manager)):
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    has_bookings = (await db.execute(
        select(RoomBooking.id).where(RoomBooking.room_id == room_id).limit(1)
    )).scalar_one_or_none()
    if has_bookings is not None:
        raise HTTPException(status_code=409, detail="Cannot delete room with existing bookings")
    await db.delete(room)
    await db.commit()