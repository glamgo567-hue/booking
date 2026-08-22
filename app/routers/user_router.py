from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_office_manager
from app.dependencies.db import get_db
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import RoleUpdate, UserRead

user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("", response_model=list[UserRead])
async def get_users(skip: int = Query(0, ge=0),
                    limit: int = Query(10, ge=1, le=100),
                    db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(require_office_manager)):
    users = (await db.execute(
        select(User).order_by(User.created_at.desc(), User.id.desc()).offset(skip).limit(limit)
    )).scalars().all()
    return users

@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int,
                   db: AsyncSession = Depends(get_db),
                   current_user: User = Depends(require_office_manager)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.patch("/{user_id}/role", response_model=UserRead)
async def role_change(user_id: int,
                      role_data: RoleUpdate,
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(require_office_manager)):
    target_user = await db.get(User, user_id)
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if role_data.role == UserRole.USER and target_user.role == UserRole.OFFICE_MANAGER:
        number_managers = (await db.execute(select(func.count(User.id)).where(User.role == UserRole.OFFICE_MANAGER))).scalar()
        if number_managers == 1:
            raise HTTPException(status_code=409, detail="There is only 1 manager left")
    target_user.role = role_data.role
    await db.commit()
    await db.refresh(target_user)
    return target_user