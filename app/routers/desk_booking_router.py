import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.commands.core import AsyncScript
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db, get_redis, get_reserve_script
from app.models.desk_booking_model import DeskBooking, DeskStatus
from app.models.user_model import User, UserRole
from app.schemas.desk_booking_schemas import DeskBookingCreate, DeskBookingRead
from app.services.desk_pool import lazy_initialization, release, reserve
from app.tasks.desk_tasks import auto_cancel_desk_booking

desk_booking_router = APIRouter(prefix="/bookings", tags=["booking"])

@desk_booking_router.post("/desks", response_model=DeskBookingRead, status_code=status.HTTP_201_CREATED)
async def create_desk_booking(desk_booking_data: DeskBookingCreate, 
                              db: AsyncSession = Depends(get_db), 
                              current_user: User = Depends(get_current_user),
                              redis_client: redis.Redis = Depends(get_redis),
                              script: AsyncScript = Depends(get_reserve_script)):

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
        countdown=10)
    return new_desk_booking

@desk_booking_router.get("/desks/me", response_model=list[DeskBookingRead])
async def get_desk_bookings_for_me(skip: int = Query(0, ge=0),
                                   limit: int = Query(10, ge=1, le=100),
                                   db: AsyncSession = Depends(get_db),
                                   current_user: User = Depends(get_current_user)):
    desk_bookings = (await db.execute(select(DeskBooking).where(DeskBooking.user_id == current_user.id).order_by(DeskBooking.date).offset(skip).limit(limit))).scalars().all()
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
    desk_booking.status = DeskStatus.CANCELLED
    await release(redis_client, desk_booking.date)
    await db.commit()

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