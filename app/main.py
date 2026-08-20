from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, status

from app.core.config import settings
from app.routers.auth_router import auth_router
from app.routers.desk_booking_router import desk_booking_router
from app.routers.desk_router import desk_router
from app.routers.room_booking_router import room_booking_router
from app.routers.room_router import room_router
from app.routers.user_router import user_router
from app.services.desk_pool import LUA_CODE


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
    app.state.reserve_script = app.state.redis.register_script(LUA_CODE)
    yield
    await app.state.redis.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}

app.include_router(auth_router)
app.include_router(desk_router)
app.include_router(room_router)
app.include_router(desk_booking_router)
app.include_router(room_booking_router)
app.include_router(user_router)