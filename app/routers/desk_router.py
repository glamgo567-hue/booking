from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_office_manager
from app.dependencies.db import get_db
from app.models.desk_model import Desk
from app.models.user_model import User
from app.schemas.desk_schemas import DeskCreate, DeskRead, DeskUpdate

desk_router = APIRouter(prefix="/desks", tags=["desk"])

@desk_router.post("", response_model=DeskRead, status_code=status.HTTP_201_CREATED)
async def create_desk(desk_data: DeskCreate, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_office_manager)):
    new_desk = Desk(floor = desk_data.floor)
    db.add(new_desk)
    await db.commit()
    await db.refresh(new_desk)
    return new_desk

@desk_router.get("", response_model=list[DeskRead])
async def get_desks(skip: int = Query(0, ge=0),
                    limit: int = Query(10, ge=1, le=100), 
                    db: AsyncSession = Depends(get_db)):
    desks = (await db.execute(select(Desk).order_by(Desk.created_at.desc(), Desk.id.desc()).offset(skip).limit(limit))).scalars().all()
    return desks

@desk_router.get("/{desk_id}", response_model=DeskRead)
async def get_desk(desk_id: int,
                   db: AsyncSession = Depends(get_db)):
    desk = await db.get(Desk, desk_id)
    if desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    return desk

@desk_router.patch("/{desk_id}", response_model=DeskRead)
async def fix_desk(desk_id: int,
                   desk_data: DeskUpdate, 
                   db: AsyncSession = Depends(get_db), 
                   current_user: User = Depends(require_office_manager)):
    desk = await db.get(Desk, desk_id)
    if desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    update_desk_data = desk_data.model_dump(exclude_unset=True)
    for field, value in update_desk_data.items():
        setattr(desk, field, value)
    await db.commit()
    await db.refresh(desk)
    return desk

@desk_router.delete("/{desk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_desk(desk_id: int, 
                      db: AsyncSession = Depends(get_db), 
                      current_user: User = Depends(require_office_manager)):
    desk = await db.get(Desk, desk_id)
    if desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    await db.delete(desk)
    await db.commit()