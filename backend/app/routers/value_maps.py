"""Value mapping CRUD endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.value_map import ValueMap
from app.models.user import User

router = APIRouter(prefix="/api/value-maps", tags=["value-maps"])


class ValueMapCreate(BaseModel):
    name: str
    mappings: dict = {}


class ValueMapUpdate(BaseModel):
    name: str | None = None
    mappings: dict | None = None


class ValueMapResponse(BaseModel):
    id: int
    name: str
    mappings: dict
    created_at: str | None = None

    class Config:
        from_attributes = True


@router.get("", response_model=list[ValueMapResponse])
async def list_maps(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ValueMap).where(ValueMap.user_id == user.id).order_by(ValueMap.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ValueMapResponse, status_code=status.HTTP_201_CREATED)
async def create_map(
    data: ValueMapCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vm = ValueMap(user_id=user.id, name=data.name, mappings=data.mappings)
    db.add(vm)
    await db.commit()
    await db.refresh(vm)
    return vm


@router.put("/{map_id}", response_model=ValueMapResponse)
async def update_map(
    map_id: int,
    data: ValueMapUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ValueMap).where(ValueMap.id == map_id, ValueMap.user_id == user.id)
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(status_code=404, detail="Value map not found")
    if data.name is not None:
        vm.name = data.name
    if data.mappings is not None:
        vm.mappings = data.mappings
    await db.commit()
    await db.refresh(vm)
    return vm


@router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_map(
    map_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ValueMap).where(ValueMap.id == map_id, ValueMap.user_id == user.id)
    )
    vm = result.scalar_one_or_none()
    if not vm:
        raise HTTPException(status_code=404, detail="Value map not found")
    await db.delete(vm)
    await db.commit()
