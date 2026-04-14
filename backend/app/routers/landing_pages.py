import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.landing_page import LandingPage
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["landing-pages"])


async def _publish_scheduled_landings(db: AsyncSession) -> int:
    """Lazy-publish landing pages whose scheduled_at has passed."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(LandingPage)
        .where(LandingPage.is_published == False)  # noqa: E712
        .where(LandingPage.scheduled_at.isnot(None))
        .where(LandingPage.scheduled_at <= now)
    )
    pages = result.scalars().all()
    for p in pages:
        p.is_published = True
        if p.published_at is None:
            p.published_at = p.scheduled_at or now
    if pages:
        await db.commit()
    return len(pages)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    replacements = {
        "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
        "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    }
    for pl, en in replacements.items():
        text = text.replace(pl, en)
    text = re.sub(r"[^a-z0-9\-/ ]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-/")


def _word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


class LandingPageBase(BaseModel):
    title: str
    slug: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    hero_image: str | None = None
    gallery: list[str] | None = None
    price: str | None = None
    price_negotiable: bool = False
    location: str | None = None
    cta_text: str | None = None
    cta_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    is_indexable: bool = True
    is_followable: bool = True
    is_published: bool = False
    scheduled_at: datetime | None = None


class LandingPageCreate(LandingPageBase):
    pass


class LandingPageUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    hero_image: str | None = None
    gallery: list[str] | None = None
    price: str | None = None
    price_negotiable: bool | None = None
    location: str | None = None
    cta_text: str | None = None
    cta_url: str | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    is_indexable: bool | None = None
    is_followable: bool | None = None
    is_published: bool | None = None
    scheduled_at: datetime | None = None


class LandingPageResponse(BaseModel):
    id: int
    user_id: int
    slug: str
    title: str
    short_description: str | None
    full_description: str | None
    hero_image: str | None
    gallery: list[str] | None
    price: str | None
    price_negotiable: bool
    location: str | None
    cta_text: str | None
    cta_url: str | None
    meta_title: str | None
    meta_description: str | None
    is_indexable: bool
    is_followable: bool
    is_published: bool
    published_at: datetime | None
    scheduled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


async def _ensure_user_page(db: AsyncSession, page_id: int, user_id: int) -> LandingPage:
    page = await db.get(LandingPage, page_id)
    if not page or page.user_id != user_id:
        raise HTTPException(status_code=404, detail="Landing page not found")
    return page


def _validate_title(title: str) -> None:
    if _word_count(title) < 3:
        raise HTTPException(status_code=400, detail="Tytuł (H1) musi mieć co najmniej 3 słowa")


def _build_slug(raw_slug: str | None, title: str, user_id: int) -> str:
    parts: list[str]
    if raw_slug:
        # If user didn't include user_id in middle, inject it.
        tokens = [t for t in raw_slug.strip("/").split("/") if t]
        if str(user_id) not in tokens and len(tokens) >= 2:
            mid = len(tokens) // 2
            tokens = tokens[:mid] + [str(user_id)] + tokens[mid:]
        elif str(user_id) not in tokens:
            tokens = tokens + [str(user_id)] + [_slugify(title) or "oferta"]
        parts = [_slugify(t) for t in tokens if t]
    else:
        parts = ["oferta", str(user_id), _slugify(title) or "oferta"]
    parts = [p for p in parts if p]
    if str(user_id) not in parts:
        parts.insert(max(len(parts) // 2, 1), str(user_id))
    return "/".join(parts)


# Authenticated user endpoints --------------------------------------------

@router.get("/landing-pages", response_model=list[LandingPageResponse])
async def list_my_pages(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LandingPage).where(LandingPage.user_id == current_user.id).order_by(LandingPage.created_at.desc())
    )
    return result.scalars().all()


@router.post("/landing-pages", response_model=LandingPageResponse, status_code=201)
async def create_page(
    data: LandingPageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_title(data.title)
    slug = _build_slug(data.slug, data.title, current_user.id)
    existing = await db.execute(select(LandingPage).where(LandingPage.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug już istnieje — zmień slug")
    payload = data.model_dump(exclude={"slug"})
    page = LandingPage(user_id=current_user.id, slug=slug, **payload)
    if page.is_published and page.published_at is None:
        page.published_at = datetime.now(timezone.utc)
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page


@router.get("/landing-pages/{page_id}", response_model=LandingPageResponse)
async def get_my_page(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _ensure_user_page(db, page_id, current_user.id)


@router.put("/landing-pages/{page_id}", response_model=LandingPageResponse)
async def update_my_page(
    page_id: int,
    data: LandingPageUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    page = await _ensure_user_page(db, page_id, current_user.id)
    updates = data.model_dump(exclude_unset=True)
    if "title" in updates and updates["title"]:
        _validate_title(updates["title"])
    if "slug" in updates:
        new_title = updates.get("title") or page.title
        new_slug = _build_slug(updates["slug"], new_title, current_user.id)
        if new_slug != page.slug:
            conflict = await db.execute(select(LandingPage).where(LandingPage.slug == new_slug, LandingPage.id != page.id))
            if conflict.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Slug już istnieje — zmień slug")
            updates["slug"] = new_slug
        else:
            updates.pop("slug")
    was_published = page.is_published
    for k, v in updates.items():
        setattr(page, k, v)
    if page.is_published and not was_published and page.published_at is None:
        page.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(page)
    return page


@router.delete("/landing-pages/{page_id}", status_code=204)
async def delete_my_page(
    page_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    page = await _ensure_user_page(db, page_id, current_user.id)
    await db.delete(page)
    await db.commit()


# Public endpoint ----------------------------------------------------------

@router.get("/landing/{slug:path}", response_model=LandingPageResponse)
async def get_public_page(slug: str, db: AsyncSession = Depends(get_db)):
    await _publish_scheduled_landings(db)
    result = await db.execute(select(LandingPage).where(LandingPage.slug == slug))
    page = result.scalar_one_or_none()
    if not page or not page.is_published:
        raise HTTPException(status_code=404, detail="Landing page not found")
    return page
