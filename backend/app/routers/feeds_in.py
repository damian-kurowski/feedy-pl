from fastapi import APIRouter, Depends, HTTPException, status
from app.services.recommendations import generate_recommendations
from pydantic import BaseModel
from sqlalchemy import String, func, select
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


_EAN_FIELD_KEYS = ["ean", "gtin", "code", "g:gtin", "@ean", "barcode", "attr:EAN", "attr:GTIN"]


def _extract_ean(product_value: dict) -> str | None:
    for key in _EAN_FIELD_KEYS:
        v = product_value.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, (int, float)):
            return str(int(v))
    return None


@router.get("/search/global")
async def global_search(
    q: str,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cross-feed search across all user's products by name, EAN, SKU, category."""
    if not q or len(q.strip()) < 2:
        return {"results": []}
    needle = f"%{q.strip().lower()}%"

    # Limit search to user's feeds
    user_feeds_res = await db.execute(
        select(FeedIn.id, FeedIn.name).where(FeedIn.user_id == current_user.id)
    )
    user_feeds = {row.id: row.name for row in user_feeds_res.all()}
    if not user_feeds:
        return {"results": []}

    # Search by product_name (cheap, indexed)
    name_res = await db.execute(
        select(ProductIn)
        .where(ProductIn.feed_in_id.in_(user_feeds.keys()))
        .where(func.lower(ProductIn.product_name).like(needle))
        .limit(limit)
    )
    name_matches = list(name_res.scalars().all())

    # Also search inside JSONB product_value for EAN/SKU/category
    if len(name_matches) < limit:
        text_res = await db.execute(
            select(ProductIn)
            .where(ProductIn.feed_in_id.in_(user_feeds.keys()))
            .where(func.lower(func.cast(ProductIn.product_value, String)).like(needle))
            .limit(limit - len(name_matches))
        )
        seen_ids = {p.id for p in name_matches}
        for p in text_res.scalars().all():
            if p.id not in seen_ids:
                name_matches.append(p)

    results = []
    for p in name_matches:
        pv = p.product_value or {}
        results.append({
            "id": p.id,
            "feed_in_id": p.feed_in_id,
            "feed_in_name": user_feeds.get(p.feed_in_id, ""),
            "product_name": p.product_name,
            "ean": pv.get("ean") or pv.get("gtin") or pv.get("code") or pv.get("g:gtin") or pv.get("attr:EAN"),
            "price": pv.get("price") or pv.get("@price") or pv.get("g:price"),
            "category": pv.get("cat") or pv.get("category") or pv.get("g:product_type"),
            "image": pv.get("image") or pv.get("img") or pv.get("g:image_link"),
            "custom_product": p.custom_product,
        })
    return {"results": results, "query": q}


@router.get("/{feed_id}/ean-report")
async def ean_report(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns EAN/GTIN coverage and validity stats for a source feed."""
    from app.services.validators.base import validate_ean

    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(select(ProductIn).where(ProductIn.feed_in_id == feed_id))
    products = result.scalars().all()

    total = len(products)
    with_ean = 0
    valid = 0
    invalid_items: list[dict] = []
    for p in products:
        raw_ean = _extract_ean(p.product_value or {})
        if not raw_ean:
            continue
        with_ean += 1
        result_dict = validate_ean(raw_ean)
        if result_dict["valid"]:
            valid += 1
        else:
            invalid_items.append({
                "id": p.id,
                "product_name": p.product_name,
                "ean": raw_ean,
                "reason": result_dict["reason"],
                "fixed": result_dict.get("fixed"),
            })

    return {
        "total_products": total,
        "with_ean": with_ean,
        "valid_ean": valid,
        "invalid_ean": with_ean - valid,
        "missing_ean": total - with_ean,
        "ean_coverage_pct": round((with_ean / total * 100), 1) if total else 0,
        "ean_validity_pct": round((valid / with_ean * 100), 1) if with_ean else 0,
        "invalid_items": invalid_items[:200],  # cap to 200 for UI
    }


class ManualProductCreate(BaseModel):
    product_name: str
    product_value: dict

class ManualProductUpdate(BaseModel):
    product_name: str | None = None
    product_value: dict | None = None


@router.post("/{feed_id}/products")
async def create_manual_product(
    feed_id: int,
    data: ManualProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed = await _get_user_feed(db, feed_id, current_user.id)
    product = ProductIn(
        feed_in_id=feed.id,
        product_name=data.product_name,
        product_value=data.product_value,
        custom_product=True,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "product_name": product.product_name, "product_value": product.product_value}


@router.put("/{feed_id}/products/{product_id}")
async def update_manual_product(
    feed_id: int,
    product_id: int,
    data: ManualProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(
        select(ProductIn).where(ProductIn.id == product_id, ProductIn.feed_in_id == feed_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.product_name is not None:
        product.product_name = data.product_name
    if data.product_value is not None:
        product.product_value = data.product_value
    await db.commit()
    await db.refresh(product)
    return {"id": product.id, "product_name": product.product_name, "product_value": product.product_value}


@router.delete("/{feed_id}/products/{product_id}", status_code=204)
async def delete_manual_product(
    feed_id: int,
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed(db, feed_id, current_user.id)
    result = await db.execute(
        select(ProductIn).where(ProductIn.id == product_id, ProductIn.feed_in_id == feed_id, ProductIn.custom_product == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not a manual product")
    await db.delete(product)
    await db.commit()


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
