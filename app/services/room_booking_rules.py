from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_booking_model import RoomBooking, RoomStatus
from app.models.room_model import Room


async def overlap_check(room_id: int,
                        start_time: datetime,
                        end_time: datetime,
                        db: AsyncSession,
                        exclude_booking_id: int | None = None) -> bool:
    booking_id_conflict = (await db.execute(select(RoomBooking.id)
                                     .where(RoomBooking.room_id == room_id, 
                                            RoomBooking.status.in_([RoomStatus.CONFIRMED, RoomStatus.PENDING]),
                                            RoomBooking.start_time < end_time,
                                            RoomBooking.end_time > start_time,
                                            RoomBooking.id != exclude_booking_id)
                                     .limit(1))).scalar_one_or_none()
    return booking_id_conflict is not None

async def lock_room(db: AsyncSession, room_id: int) -> Room | None:
    room = (await db.execute(select(Room).where(Room.id == room_id).with_for_update())).scalar_one_or_none()
    return room 
    