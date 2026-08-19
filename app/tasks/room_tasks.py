import asyncio

from app.celery_app import celery_app
from app.dependencies.db import async_session_maker
from app.models.room_booking_model import RoomBooking, RoomStatus


@celery_app.task
def auto_cancel_room_booking(booking_id: int) -> None:
    asyncio.run(_auto_cancel(booking_id))

async def _auto_cancel(booking_id: int) -> None:
    async with async_session_maker() as db:
        room_booking = await db.get(RoomBooking, booking_id)
        if room_booking is None:
            return 
        if room_booking.status != RoomStatus.PENDING:
            return
        room_booking.status = RoomStatus.CANCELLED
        await db.commit()