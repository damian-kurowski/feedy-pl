"""Competitor price tracking endpoints (Pro feature).

Lets users compare their prices against Ceneo competition for products
with valid EAN codes. Snapshots are persisted in data.competitor_price_snapshots
so we can chart trends over time and avoid re-scraping fresh data.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.competitor_price import CompetitorPriceSnapshot
from app.models.feed_in import FeedIn
from app.models.product import ProductIn
from app.models.user import User
from app.services.ceneo_scraper import search_by_ean

router = APIRouter(prefix="/api/competitor-prices", tags=["competitor-prices"])

PRO_PLAN_IDS = {3, 4, 99}  # Pro, Business, Unlimited
SCRAPE_FRESH_HOURS = 24


def _require_pro(user: User) -> None:
    plan_id = user.plan_id if user.plan_id is not None else 1
    if plan_id not in PRO_PLAN_IDS:
        raise HTTPException(
            status_code=403,
            detail="Śledzenie konkurencji jest dostępne w planie Pro i wyższych. Przejdź do cennika, aby zobaczyć opcje upgrade.",
        )


_EAN_FIELDS = ["ean", "gtin", "code", "g:gtin", "@ean", "barcode", "attr:EAN", "attr:GTIN"]


def _extract_ean(pv: dict) -> str | None:
    if not pv:
        return None
    for k in _EAN_FIELDS:
        v = pv.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, (int, float)):
            return str(int(v))
    return None


def _extract_price(pv: dict) -> float | None:
    if not pv:
        return None
    for k in ("price", "@price", "g:price", "cena"):
        v = pv.get(k)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(" ", "").replace(",", ".")
        # Strip currency suffix like "PLN"
        s = "".join(ch for ch in s if ch.isdigit() or ch == ".")
        try:
            return float(s)
        except ValueError:
            continue
    return None


@router.get("/feed/{feed_in_id}")
async def list_feed_competitor_prices(
    feed_in_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return latest competitor snapshots for all products in a feed."""
    _require_pro(current_user)

    feed_result = await db.execute(
        select(FeedIn).where(FeedIn.id == feed_in_id, FeedIn.user_id == current_user.id)
    )
    feed = feed_result.scalar_one_or_none()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed nie znaleziony")

    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_in_id)
    )
    products = list(products_result.scalars().all())

    # Latest snapshot per product
    snap_result = await db.execute(
        select(CompetitorPriceSnapshot)
        .where(CompetitorPriceSnapshot.product_in_id.in_([p.id for p in products]))
        .order_by(CompetitorPriceSnapshot.scraped_at.desc())
    )
    snaps = list(snap_result.scalars().all())
    latest_per_product: dict[int, CompetitorPriceSnapshot] = {}
    for s in snaps:
        if s.product_in_id not in latest_per_product:
            latest_per_product[s.product_in_id] = s

    # Aggregate stats
    items = []
    losing = 0  # products where our price > lowest competitor
    winning = 0
    no_data = 0
    for p in products:
        ean = _extract_ean(p.product_value or {})
        our_price = _extract_price(p.product_value or {})
        snap = latest_per_product.get(p.id)
        if not snap:
            no_data += 1
            items.append({
                "product_id": p.id,
                "product_name": p.product_name,
                "ean": ean,
                "our_price": our_price,
                "lowest_price": None,
                "lowest_seller": None,
                "our_position": None,
                "total_offers": None,
                "scraped_at": None,
                "diff_pct": None,
                "status": "unknown",
            })
            continue

        lowest = float(snap.lowest_price) if snap.lowest_price is not None else None
        ours = float(snap.our_price) if snap.our_price is not None else our_price
        diff_pct: float | None = None
        if ours and lowest:
            diff_pct = round(((ours - lowest) / lowest) * 100, 1)
        if ours and lowest and ours > lowest:
            status = "losing"
            losing += 1
        elif ours and lowest and ours <= lowest:
            status = "winning"
            winning += 1
        else:
            status = "unknown"

        items.append({
            "product_id": p.id,
            "product_name": p.product_name,
            "ean": ean,
            "our_price": ours,
            "lowest_price": lowest,
            "lowest_seller": snap.lowest_seller,
            "our_position": snap.our_position,
            "total_offers": snap.total_offers,
            "scraped_at": snap.scraped_at.isoformat() if snap.scraped_at else None,
            "diff_pct": diff_pct,
            "status": status,
        })

    return {
        "feed_in_id": feed_in_id,
        "total_products": len(products),
        "with_snapshots": len(items) - no_data,
        "winning": winning,
        "losing": losing,
        "no_data": no_data,
        "items": items,
    }


@router.post("/feed/{feed_in_id}/scrape")
async def scrape_feed_competitor_prices(
    feed_in_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Scrape Ceneo for products with EAN that haven't been scraped in 24h.

    Throttled (~2s per request); use a small `limit` per request.
    """
    _require_pro(current_user)

    feed_result = await db.execute(
        select(FeedIn).where(FeedIn.id == feed_in_id, FeedIn.user_id == current_user.id)
    )
    feed = feed_result.scalar_one_or_none()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed nie znaleziony")

    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_in_id)
    )
    products = list(products_result.scalars().all())

    fresh_threshold = datetime.now(timezone.utc) - timedelta(hours=SCRAPE_FRESH_HOURS)

    # Filter: only products with EAN, no recent snapshot
    queue = []
    for p in products:
        ean = _extract_ean(p.product_value or {})
        if not ean:
            continue
        recent_q = await db.execute(
            select(CompetitorPriceSnapshot)
            .where(CompetitorPriceSnapshot.product_in_id == p.id)
            .where(CompetitorPriceSnapshot.scraped_at >= fresh_threshold)
            .limit(1)
        )
        if recent_q.scalar_one_or_none() is None:
            queue.append((p, ean))
        if len(queue) >= limit:
            break

    scraped = 0
    failed = 0
    for product, ean in queue:
        result = await search_by_ean(ean)
        if result.error:
            failed += 1
            continue
        our_price = _extract_price(product.product_value or {})
        snap = CompetitorPriceSnapshot(
            product_in_id=product.id,
            ean=ean,
            our_price=our_price,
            lowest_price=result.lowest_price,
            lowest_seller=result.lowest_seller,
            our_position=None,  # we don't know our exact ranking yet (would need our seller name)
            total_offers=result.total_offers,
            offers=[{"seller": o.seller, "price": o.price} for o in result.offers],
        )
        db.add(snap)
        scraped += 1

    if scraped:
        await db.commit()

    return {
        "queued": len(queue),
        "scraped": scraped,
        "failed": failed,
        "remaining_to_scrape": max(0, sum(
            1 for p in products if _extract_ean(p.product_value or {})
        ) - scraped - failed - len(queue) + len(queue)),
    }
