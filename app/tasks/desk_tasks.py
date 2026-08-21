import asyncio

import redis.asyncio as redis

from app.celery_app import celery_app
from app.core.config import settings
from app.dependencies.db import async_session_maker
from app.models.desk_booking_model import DeskBooking, DeskStatus
from app.services.desk_pool import release


@celery_app.task
def auto_cancel_desk_booking(booking_id: int) -> None:
    asyncio.run(_auto_cancel(booking_id))

async def _auto_cancel(booking_id: int) -> None:
    async with async_session_maker() as db:
        desk_booking = await db.get(DeskBooking, booking_id)
        if desk_booking is None:
            return 
        if desk_booking.status != DeskStatus.PENDING:
            return
        desk_booking.status = DeskStatus.CANCELLED
        await db.commit()
        redis_client = redis.Redis.from_url(settings.redis_url)
        try:
            await release(redis_client, desk_booking.date)
        finally:
            await redis_client.aclose()