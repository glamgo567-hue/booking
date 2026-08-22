from datetime import date as date_

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.commands.core import AsyncScript
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.dependencies.auth import get_current_user, require_office_manager
from app.dependencies.db import get_db, get_redis, get_reserve_script
from app.models.desk_booking_model import DeskBooking, DeskStatus
from app.models.user_model import User, UserRole
from app.schemas.desk_booking_schemas import DeskBookingCreate, DeskBookingRead
from app.schemas.desk_schemas import DeskAvailability
from app.services.desk_pool import (
    get_available,
    get_available_range,
    lazy_initialization,
    release,
    reserve,
)
from app.tasks.desk_tasks import auto_cancel_desk_booking

desk_booking_router = APIRouter(prefix="/bookings", tags=["booking"])

@desk_booking_router.post("/desks", response_model=DeskBookingRead, status_code=status.HTTP_201_CREATED)
async def create_desk_booking(desk_booking_data: DeskBookingCreate, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(get_current_user),
                              redis_client: redis.Redis = Depends(get_redis),
                              script: AsyncScript = Depends(get_reserve_script)):

    existing = (await db.execute(
    select(DeskBooking).where(
        DeskBooking.user_id == current_user.id,
        DeskBooking.date == desk_booking_data.date,
        DeskBooking.status.in_([DeskStatus.CONFIRMED, DeskStatus.PENDING]),))).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(409, "You already have a booking for this date")

    await lazy_initialization(db, redis_client, desk_booking_data.date)
    if not await reserve(script, desk_booking_data.date):
        raise HTTPException(409, "No desks available for this date")
    new_desk_booking = DeskBooking(date=desk_booking_data.date,
                                   user_id=current_user.id,
                                   status=DeskStatus.PENDING)
    try:
        db.add(new_desk_booking)
        await db.commit()
    except SQLAlchemyError:
        await release(redis_client, desk_booking_data.date)
        raise HTTPException(500)
    await db.refresh(new_desk_booking)
    auto_cancel_desk_booking.apply_async(
        args=[new_desk_booking.id],
        countdown=settings.booking_auto_cancel_seconds)
    return new_desk_booking

@desk_booking_router.get("/desks/availability", response_model=DeskAvailability)
async def get_desk_availability(date: date_ = Query(...),
                                db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(get_current_user),
                                redis_client: redis.Redis = Depends(get_redis)):
    available = await get_available(db, redis_client, date)
    return DeskAvailability(date=date, available=available)

@desk_booking_router.get("/desks/availability/range", response_model=list[DeskAvailability])
async def get_desk_availability_range(date_from: date_ = Query(...),
                                      date_to: date_ = Query(...),
                                      db: AsyncSession = Depends(get_db),
                                      current_user: User = Depends(get_current_user),
                                      redis_client: redis.Redis = Depends(get_redis)):
    if date_to < date_from:
        raise HTTPException(status_code=422, detail="date_to must not be earlier than date_from")
    if (date_to - date_from).days > 92:
        raise HTTPException(status_code=422, detail="Range must not exceed 93 days")
    available = await get_available_range(db, redis_client, date_from, date_to)
    return [DeskAvailability(date=booking_date, available=count) for booking_date, count in available.items()]

@desk_booking_router.get("/desks/me", response_model=list[DeskBookingRead])
async def get_desk_bookings_for_me(skip: int = Query(0, ge=0),
                                   limit: int = Query(10, ge=1, le=100),
                                   db: AsyncSession = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    desk_bookings = (await db.execute(select(DeskBooking).where(DeskBooking.user_id == current_user.id).order_by(DeskBooking.date).offset(skip).limit(limit))).scalars().all()
    return desk_bookings

@desk_booking_router.get("/desks", response_model=list[DeskBookingRead])
async def get_all_desk_bookings(date: date_ | None = Query(None),
                                skip: int = Query(0, ge=0),
                                limit: int = Query(10, ge=1, le=100),
                                db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(require_office_manager)):
    query = select(DeskBooking).where(
        DeskBooking.status.in_([DeskStatus.CONFIRMED, DeskStatus.PENDING]),
    )
    if date is not None:
        query = query.where(DeskBooking.date == date)
    desk_bookings = (await db.execute(
        query.order_by(DeskBooking.date).offset(skip).limit(limit)
    )).scalars().all()
    return desk_bookings

@desk_booking_router.delete("/desks/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_desk_booking(booking_id: int, 
                              db: AsyncSession = Depends(get_db),
                              redis_client: redis.Redis = Depends(get_redis), 
                              current_user: User = Depends(get_current_user)):
    desk_booking = await db.get(DeskBooking, booking_id)
    if desk_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if desk_booking.user_id != current_user.id and current_user.role != UserRole.OFFICE_MANAGER:
        raise HTTPException(status_code=403, detail="No rights")
    if desk_booking.status == DeskStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Booking already cancelled")

    desk_booking.status = DeskStatus.CANCELLED
    await db.commit()
    await release(redis_client, desk_booking.date)

@desk_booking_router.patch("/desks/{booking_id}/confirm", response_model=DeskBookingRead)
async def confirm_endpoint(booking_id: int, 
                           db: AsyncSession = Depends(get_db), 
                           current_user: User = Depends(get_current_user)):
    desk_booking = await db.get(DeskBooking, booking_id)
    if desk_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if desk_booking.user_id != current_user.id: 
        raise HTTPException(status_code=403, detail="No rights")
    if desk_booking.status != DeskStatus.PENDING:
        raise HTTPException(status_code=409, detail="Booking is not active")
    desk_booking.status = DeskStatus.CONFIRMED
    await db.commit()
    await db.refresh(desk_booking)
    return desk_booking