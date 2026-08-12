from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.user_model import User
from app.schemas.user_schemas import Token, UserRead, UserRegister

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def registration(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(or_(User.username==user_data.username, User.email==user_data.email)))).scalar_one_or_none()
    if user is not None:
        raise HTTPException(status_code=409, detail="Username or email is already occupied")
    new_hashed_password = hash_password(user_data.password)
    new_user = User(username = user_data.username,
                    email = user_data.email,
                    hashed_password = new_hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username==form_data.username))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    verify = verify_password(form_data.password, user.hashed_password)
    if not verify:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": str(user.id)})
    log_token = Token(access_token= token, token_type="bearer")
    return log_token

@auth_router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user