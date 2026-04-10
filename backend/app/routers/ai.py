"""AI description rewriting endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.feed_out import FeedOut
from app.models.product import ProductIn
from app.models.product_override import ProductOverride
from app.models.user import User
from app.services.ai_service import is_ai_available, rewrite_descriptions_bulk

router = APIRouter(prefix="/api/feeds-out", tags=["ai"])


class RewriteRequest(BaseModel):
    limit: int = 10


class ApplyRewriteItem(BaseModel):
    product_id: int
    field: str = "desc"
    value: str


class ApplyRewriteRequest(BaseModel):
    rewrites: list[ApplyRewriteItem]


async def _get_user_feed_out(db: AsyncSession, feed_out_id: int, user_id: int) -> FeedOut:
    result = await db.execute(
        select(FeedOut).where(FeedOut.id == feed_out_id, FeedOut.user_id == user_id)
    )
    feed_out = result.scalar_one_or_none()
    if not feed_out:
        raise HTTPException(status_code=404, detail="Feed out not found")
    return feed_out


@router.post("/{feed_out_id}/ai-rewrite")
async def ai_rewrite_preview(
    feed_out_id: int,
    body: RewriteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not is_ai_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable — ANTHROPIC_API_KEY not configured",
        )

    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id).limit(body.limit)
    )
    products = [
        {"id": p.id, "product_name": p.product_name, "product_value": p.product_value}
        for p in products_result.scalars().all()
    ]

    results = await rewrite_descriptions_bulk(products, feed_out.type, limit=body.limit)
    return {"rewrites": results}


@router.post("/{feed_out_id}/ai-rewrite/apply")
async def ai_rewrite_apply(
    feed_out_id: int,
    body: ApplyRewriteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    applied = 0
    for item in body.rewrites:
        # Upsert override
        existing = await db.execute(
            select(ProductOverride).where(
                ProductOverride.feed_out_id == feed_out_id,
                ProductOverride.product_in_id == item.product_id,
            )
        )
        override = existing.scalar_one_or_none()
        if override:
            overrides = override.field_overrides or {}
            overrides[item.field] = item.value
            override.field_overrides = overrides
        else:
            override = ProductOverride(
                feed_out_id=feed_out_id,
                product_in_id=item.product_id,
                field_overrides={item.field: item.value},
                excluded=False,
            )
            db.add(override)
        applied += 1

    await db.commit()
    return {"applied": applied}
