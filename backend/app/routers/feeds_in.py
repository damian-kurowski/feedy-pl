from fastapi import APIRouter, Depends, HTTPException, status
from app.services.recommendations import generate_recommendations
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.feed_in import FeedIn
from app.models.feed_out import FeedOut
from app.models.product import ProductIn
from app.models.user import User
from app.models.feed_change_log import FeedChangeLog
from app.models.xml_element import XmlElementIn
from app.schemas.feed_in import (
    FeedInCreate,
    FeedInResponse,
    FeedInUpdate,
    ProductResponse,
    XmlElementResponse,
)

router = APIRouter(prefix="/api/feeds-in", tags=["feeds-in"])


@router.get("/analytics/summary")
async def feeds_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics summary for all user's feeds."""
    feeds_result = await db.execute(
        select(FeedIn).where(FeedIn.user_id == current_user.id)
    )
    feeds = feeds_result.scalars().all()

    total_products = 0
    feeds_ok = 0
    feeds_error = 0
    feeds_pending = 0

    feed_details = []
    for feed in feeds:
        count_result = await db.execute(
            select(func.count()).select_from(ProductIn).where(ProductIn.feed_in_id == feed.id)
        )
        count = count_result.scalar() or 0
        total_products += count

        if feed.fetch_status == "success":
            feeds_ok += 1
        elif feed.fetch_status == "error":
            feeds_error += 1
        else:
            feeds_pending += 1

        feed_details.append({
            "id": feed.id,
            "name": feed.name,
            "status": feed.fetch_status,
            "product_count": count,
            "last_fetched_at": feed.last_fetched_at.isoformat() if feed.last_fetched_at else None,
            "error": feed.fetch_error,
        })

    # Count feeds out
    out_result = await db.execute(
        select(func.count()).select_from(FeedOut).where(FeedOut.user_id == current_user.id)
    )
    total_feeds_out = out_result.scalar() or 0

    active_out_result = await db.execute(
        select(func.count()).select_from(FeedOut).where(
            FeedOut.user_id == current_user.id, FeedOut.active == True
        )
    )
    active_feeds_out = active_out_result.scalar() or 0

    return {
        "total_feeds_in": len(feeds),
        "total_feeds_out": total_feeds_out,
        "active_feeds_out": active_feeds_out,
        "total_products": total_products,
        "feeds_ok": feeds_ok,
        "feeds_error": feeds_error,
        "feeds_pending": feeds_pending,
        "feeds": feed_details,
    }


@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await generate_recommendations(db, current_user.id)


async def _get_user_feed(db: AsyncSession, feed_id: int, user_id: int) -> FeedIn:
    result = await db.execute(
        select(FeedIn).where(FeedIn.id == feed_id, FeedIn.user_id == user_id)
    )
    feed = result.scalar_one_or_none()
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found",
        )
    return feed


@router.get("", response_model=list[FeedInResponse])
async def list_feeds(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeedIn)
        .where(FeedIn.user_id == current_user.id)
        .order_by(FeedIn.created_at.desc())
    )
    feeds = result.scalars().all()

    response = []
    for feed in feeds:
        count_result = await db.execute(
            select(func.count()).select_from(ProductIn).where(ProductIn.feed_in_id == feed.id)
        )
        count = count_result.scalar() or 0
        feed_dict = FeedInResponse.model_validate(feed).model_dump()
        feed_dict["product_count"] = count
        response.append(feed_dict)

    return response


@router.post("", response_model=FeedInResponse, status_code=status.HTTP_201_CREATED)
async def create_feed(
    data: FeedInCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = FeedIn(
        name=data.name,
        source_url=data.source_url,
        user_id=current_user.id,
    )
    db.add(feed)
    await db.commit()
    await db.refresh(feed)
    return feed


@router.get("/{feed_id}", response_model=FeedInResponse)
async def get_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_user_feed(db, feed_id, current_user.id)


@router.put("/{feed_id}", response_model=FeedInResponse)
async def update_feed(
    feed_id: int,
    data: FeedInUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = await _get_user_feed(db, feed_id, current_user.id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(feed, key, value)
    await db.commit()
    await db.refresh(feed)
    return feed


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = await _get_user_feed(db, feed_id, current_user.id)
    await db.delete(feed)
    await db.commit()


@router.post("/{feed_id}/fetch", status_code=status.HTTP_202_ACCEPTED)
async def fetch_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = await _get_user_feed(db, feed_id, current_user.id)
    feed.fetch_status = "pending"
    await db.commit()

    # Run synchronously (no Celery worker needed)
    from app.tasks.feed_tasks import fetch_and_parse_sync
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import settings

    engine = create_engine(settings.database_url_sync)
    SessionLocal = sessionmaker(bind=engine)
    sync_session = SessionLocal()
    try:
        fetch_and_parse_sync(sync_session, feed.id)
    finally:
        sync_session.close()
        engine.dispose()
    return {"task_id": None, "status": "completed"}


@router.get("/{feed_id}/elements", response_model=list[XmlElementResponse])
async def list_elements(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(
        select(XmlElementIn).where(XmlElementIn.feed_in_id == feed_id)
    )
    return result.scalars().all()


@router.get("/{feed_id}/products", response_model=list[ProductResponse])
async def list_products(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_id)
    )
    return result.scalars().all()


@router.get("/{feed_id}/changelog")
async def list_changelog(
    feed_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(
        select(FeedChangeLog)
        .where(FeedChangeLog.feed_in_id == feed_id)
        .order_by(FeedChangeLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    changes = result.scalars().all()
    count_result = await db.execute(
        select(func.count()).select_from(FeedChangeLog).where(FeedChangeLog.feed_in_id == feed_id)
    )
    total = count_result.scalar()
    return {
        "changes": [
            {
                "id": c.id,
                "change_type": c.change_type,
                "product_name": c.product_name,
                "details": c.details,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in changes
        ],
        "total": total,
    }
