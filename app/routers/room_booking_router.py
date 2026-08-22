from datetime import date as date_
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.room_booking_model import RoomBooking, RoomStatus
from app.models.room_model import Room
from app.models.user_model import User, UserRole
from app.schemas.room_booking_schemas import (
    RoomBookingCreate,
    RoomBookingRead,
    RoomBookingReschedule,
)
from app.services.room_booking_rules import lock_room, overlap_check
from app.tasks.room_tasks import auto_cancel_room_booking

room_booking_router = APIRouter(prefix="/bookings", tags=["booking"])

@room_booking_router.post("/rooms", response_model=RoomBookingRead, status_code=status.HTTP_201_CREATED)
async def create_room_booking(room_booking_data: RoomBookingCreate, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(get_current_user)):

    room = await lock_room(db, room_booking_data.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    room_exist = await overlap_check(room_booking_data.room_id, room_booking_data.start_time, room_booking_data.end_time, db)
    if room_exist:
        raise HTTPException(409, "Room already booked for this time range")
    new_room_booking = RoomBooking(room_id=room_booking_data.room_id,
                                   start_time=room_booking_data.start_time,
                                   end_time=room_booking_data.end_time,
                                   user_id=current_user.id,
                                   status=RoomStatus.PENDING)
    db.add(new_room_booking)
    await db.commit()
    await db.refresh(new_room_booking)
    auto_cancel_room_booking.apply_async(
        args=[new_room_booking.id],
        countdown=settings.booking_auto_cancel_seconds)
    return new_room_booking

@room_booking_router.get("/rooms/me", response_model=list[RoomBookingRead])
async def get_room_bookings_for_me(skip: int = Query(0, ge=0),
                                   limit: int = Query(10, ge=1, le=100),
                                   db: AsyncSession = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    room_bookings = (await db.execute(select(RoomBooking).where(RoomBooking.user_id == current_user.id).order_by(RoomBooking.start_time).offset(skip).limit(limit))).scalars().all()
    return room_bookings

@room_booking_router.get("/rooms/{room_id}", response_model=list[RoomBookingRead])
async def get_room_bookings(room_id: int, 
                            date: date_ | None = Query(None),
                            skip: int = Query(0, ge=0),
                            limit: int = Query(10, ge=1, le=100),
                            db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    room = await db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    query = select(RoomBooking).where(
        RoomBooking.room_id == room_id,
        RoomBooking.status.in_([RoomStatus.CONFIRMED, RoomStatus.PENDING]),
    )
    if date is not None:
        day_start = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        day_end = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)
        query = query.where(RoomBooking.start_time <= day_end, RoomBooking.end_time >= day_start)
    room_bookings = (await db.execute(
        query.order_by(RoomBooking.start_time).offset(skip).limit(limit)
    )).scalars().all()
    return room_bookings

@room_booking_router.patch("/rooms/{booking_id}", response_model=RoomBookingRead)
async def patch_reschedule(booking_id: int,
                           reschedule_data: RoomBookingReschedule, 
                           db: AsyncSession = Depends(get_db), 
                           current_user: User = Depends(get_current_user)):
    room_booking = await db.get(RoomBooking, booking_id)
    if room_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if room_booking.user_id != current_user.id and current_user.role != UserRole.OFFICE_MANAGER: 
        raise HTTPException(status_code=403, detail="No rights")
    if room_booking.status != RoomStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail="Booking is not active")
    room = await lock_room(db, room_booking.room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    has_conflict = await overlap_check(room_booking.room_id, reschedule_data.start_time, reschedule_data.end_time, db, exclude_booking_id=booking_id)
    if has_conflict:
        raise HTTPException(status_code=409, detail="Selected time slot is unavailable")
    update_time_room_booking = reschedule_data.model_dump()
    for field, value in update_time_room_booking.items():
        setattr(room_booking, field, value)
    await db.commit()
    await db.refresh(room_booking)
    return room_booking

@room_booking_router.delete("/rooms/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_booking(booking_id: int, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(get_current_user)):
    room_booking = await db.get(RoomBooking, booking_id)
    if room_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if room_booking.user_id != current_user.id and current_user.role != UserRole.OFFICE_MANAGER: 
        raise HTTPException(status_code=403, detail="No rights")
    if room_booking.status == RoomStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Booking already cancelled")
    room_booking.status = RoomStatus.CANCELLED
    await db.commit()

@room_booking_router.patch("/rooms/{booking_id}/confirm", response_model=RoomBookingRead)
async def confirm_endpoint(booking_id: int, 
                           db: AsyncSession = Depends(get_db), 
                           current_user: User = Depends(get_current_user)):
    room_booking = await db.get(RoomBooking, booking_id)
    if room_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if room_booking.user_id != current_user.id: 
        raise HTTPException(status_code=403, detail="No rights")
    if room_booking.status != RoomStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking is not active")
    room_booking.status = RoomStatus.CONFIRMED
    await db.commit()
    await db.refresh(room_booking)
    return room_booking