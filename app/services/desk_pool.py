from datetime import date, timedelta

import redis.asyncio as redis
from redis.commands.core import AsyncScript
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.desk_model import Desk

LUA_CODE = """
local current = redis.call('GET', KEYS[1])
if current == false then
    return -1
end
local current_number = tonumber(current)
if current_number > 0 then
    redis.call('DECR', KEYS[1])
    return 1
else
    return 0
end
"""

def key_builder(booking_date: date) -> str:
    return f"desk_pool:{booking_date}"

async def count_active_desks(db: AsyncSession) -> int:
    return (await db.execute(select(func.count(Desk.id)).where(Desk.is_active.is_(True)))).scalar_one()

async def lazy_initialization(db: AsyncSession, 
                              redis_client: redis.Redis,
                              booking_date: date) -> None:
    desks_count_active = await count_active_desks(db)
    await redis_client.set(key_builder(booking_date), desks_count_active, nx=True)

async def get_available(db: AsyncSession,
                        redis_client: redis.Redis,
                        booking_date: date) -> int:
    current = await redis_client.get(key_builder(booking_date))
    if current is None:
        return await count_active_desks(db)
    return int(current)

async def get_available_range(db: AsyncSession,
                              redis_client: redis.Redis,
                              date_from: date,
                              date_to: date) -> dict[date, int]:
    dates = [date_from + timedelta(days=offset) for offset in range((date_to - date_from).days + 1)]
    current = await redis_client.mget([key_builder(booking_date) for booking_date in dates])
    desks_count_active = None
    available = {}
    for index, booking_date in enumerate(dates):
        if current[index] is None:
            if desks_count_active is None:
                desks_count_active = await count_active_desks(db)
            available[booking_date] = desks_count_active
        else:
            available[booking_date] = int(current[index])
    return available

async def reserve(script: AsyncScript,
                  booking_date: date) -> bool:
    result = await script(keys=[key_builder(booking_date)])
    if result == -1:
        raise RuntimeError("Desk pool key missing — lazy_initialization was not called")
    return result == 1

async def release(redis_client: redis.Redis,
                  booking_date: date) -> None:
    await redis_client.incr(key_builder(booking_date))