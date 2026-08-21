from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

import pytest
import redis.asyncio as redis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.dependencies.db import get_db, get_redis, get_reserve_script
from app.main import app
from app.models.base_model import Base
from app.services.desk_pool import LUA_CODE

engine = create_async_engine(settings.database_url)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,)

async def override_get_db():
    async with async_session_maker() as session:
        yield session

def override_get_redis():
    return redis_client

def override_get_reserve_script():
    return reserve_script

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_redis] = override_get_redis
app.dependency_overrides[get_reserve_script] = override_get_reserve_script

@pytest.fixture
async def db_schema():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

redis_client = redis.Redis.from_url(settings.redis_url)

reserve_script = redis_client.register_script(LUA_CODE)

@pytest.fixture(autouse=True)
async def flushdb():
    await redis_client.flushdb()
    yield

@pytest.fixture
async def client(db_schema):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client):
    payload_auth = {"username": "glamgo2",
                    "email": "glamgo@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)

    payload_log = {"username":"glamgo2",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)

    token_data = response_log.json()
    token = token_data.get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def dop_auth_headers(client):
    payload_auth = {"username": "glamgo3",
                    "email": "glamgo3@gmail.com",
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)

    payload_log = {"username":"glamgo3",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)

    token_data = response_log.json()
    token = token_data.get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def admin_auth_headers(client):
    payload_auth = {"username": "admin_glamgo2",
                    "email": settings.initial_admin_email,
                    "password": "111111111",
                    "confirm_password": "111111111"}
    await client.post("/auth/register", json=payload_auth)

    payload_log = {"username":"admin_glamgo2",
                    "password":"111111111"}
    response_log = await client.post("/auth/login", data=payload_log)

    token_data = response_log.json()
    token = token_data.get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def room(client, admin_auth_headers):
    payload_room = {"name": "test_room",
                    "capacity": 10}

    response_create_room = await client.post("/rooms", json=payload_room, headers=admin_auth_headers)
    assert response_create_room.status_code == 201
    return response_create_room.json()