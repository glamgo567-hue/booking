import redis.asyncio as redis
from fastapi import Request
from redis.commands.core import AsyncScript
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url, connect_args={"statement_cache_size": 0})
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,)

async def get_db():
    async with async_session_maker() as session:
        yield session

def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis

def get_reserve_script(request: Request) -> AsyncScript:
    return request.app.state.reserve_script