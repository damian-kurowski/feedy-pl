from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.notification import UserNotification
from app.models.user import User

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    created_at: datetime
    type: str
    title: str
    body: str | None
    link: str | None
    read_at: datetime | None
    model_config = {"from_attributes": True}


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    limit: int = 50,
    only_unread: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(UserNotification).where(UserNotification.user_id == current_user.id)
    if only_unread:
        q = q.where(UserNotification.read_at.is_(None))
    q = q.order_by(UserNotification.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(func.count())
        .select_from(UserNotification)
        .where(UserNotification.user_id == current_user.id)
        .where(UserNotification.read_at.is_(None))
    )
    return {"count": result.scalar() or 0}


@router.post("/{nid}/read", status_code=204)
async def mark_read(
    nid: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await db.get(UserNotification, nid)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    if note.read_at is None:
        note.read_at = datetime.now(timezone.utc)
        await db.commit()


@router.post("/read-all", status_code=204)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserNotification)
        .where(UserNotification.user_id == current_user.id)
        .where(UserNotification.read_at.is_(None))
    )
    now = datetime.now(timezone.utc)
    for n in result.scalars().all():
        n.read_at = now
    await db.commit()


@router.delete("/{nid}", status_code=204)
async def delete_notification(
    nid: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = await db.get(UserNotification, nid)
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(note)
    await db.commit()


# Helper for other modules to push notifications
async def push_notification(
    db: AsyncSession,
    user_id: int,
    *,
    type: str,
    title: str,
    body: str | None = None,
    link: str | None = None,
) -> UserNotification:
    note = UserNotification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        link=link,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note
