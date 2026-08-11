from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.dependencies.db import get_db
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    sub = payload.get("sub")
    if sub is None or not sub.isdigit():
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user_id = int(sub)
    query = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if query is None:
        raise HTTPException(status_code=401, detail="User not found")
    return query

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional),
                                    db: AsyncSession = Depends(get_db)):
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None or not sub.isdigit():
        return None
    user_id = int(sub)
    query = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if query is None:
        return None
    return query