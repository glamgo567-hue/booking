from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_office_manager
from app.dependencies.db import get_db
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import RoleUpdate, UserRead

user_router = APIRouter(prefix="/users", tags=["users"])

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