from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.blog_post import BlogPost
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["blog"])


async def _publish_scheduled(db: AsyncSession) -> int:
    """Lazy-publish any blog posts whose scheduled_at has passed."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.is_published == False)  # noqa: E712
        .where(BlogPost.scheduled_at.isnot(None))
        .where(BlogPost.scheduled_at <= now)
    )
    posts = result.scalars().all()
    for p in posts:
        p.is_published = True
        if p.published_at is None:
            p.published_at = p.scheduled_at or now
    if posts:
        await db.commit()
    return len(posts)


class BlogPostCreate(BaseModel):
    slug: str
    title: str
    html: str
    is_published: bool = False
    scheduled_at: datetime | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    is_indexable: bool = True
    is_followable: bool = True
    hero_image_path: str | None = None
    hero_image_alt: str | None = None
    og_image_path: str | None = None
    reading_minutes: int | None = None
    category: str | None = None
    excerpt: str | None = None


class BlogPostUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    html: str | None = None
    is_published: bool | None = None
    scheduled_at: datetime | None = None
    meta_title: str | None = None
    meta_description: str | None = None
    is_indexable: bool | None = None
    is_followable: bool | None = None
    hero_image_path: str | None = None
    hero_image_alt: str | None = None
    og_image_path: str | None = None
    reading_minutes: int | None = None
    category: str | None = None
    excerpt: str | None = None


class BlogPostResponse(BaseModel):
    id: int
    slug: str
    title: str
    html: str
    is_published: bool
    published_at: datetime | None
    scheduled_at: datetime | None
    meta_title: str | None
    meta_description: str | None
    is_indexable: bool
    is_followable: bool
    hero_image_path: str | None
    hero_image_alt: str | None
    og_image_path: str | None
    reading_minutes: int | None
    category: str | None
    excerpt: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlogPostListItem(BaseModel):
    id: int
    slug: str
    title: str
    published_at: datetime | None
    hero_image_path: str | None
    hero_image_alt: str | None
    reading_minutes: int | None
    category: str | None
    excerpt: str | None
    meta_description: str | None

    model_config = {"from_attributes": True}


# Public endpoints ---------------------------------------------------------

@router.get("/blog", response_model=list[BlogPostListItem])
async def list_public_posts(db: AsyncSession = Depends(get_db)):
    await _publish_scheduled(db)
    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.is_published == True)  # noqa: E712
        .order_by(BlogPost.published_at.desc().nulls_last(), BlogPost.created_at.desc())
    )
    return result.scalars().all()


@router.get("/blog/{slug}", response_model=BlogPostResponse)
async def get_public_post(slug: str, db: AsyncSession = Depends(get_db)):
    await _publish_scheduled(db)
    result = await db.execute(select(BlogPost).where(BlogPost.slug == slug))
    post = result.scalar_one_or_none()
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


# Admin endpoints ----------------------------------------------------------

STAFF_EMAILS = {"test@feedy.pl", "kurowsski@gmail.com", "admin@feedy.pl"}


def _require_staff(user: User) -> None:
    if not user or user.email not in STAFF_EMAILS:
        raise HTTPException(status_code=403, detail="Staff only")


@router.get("/admin/blog", response_model=list[BlogPostResponse])
async def list_admin_posts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    result = await db.execute(select(BlogPost).order_by(BlogPost.created_at.desc()))
    return result.scalars().all()


@router.post("/admin/blog", response_model=BlogPostResponse, status_code=201)
async def create_admin_post(
    data: BlogPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    existing = await db.execute(select(BlogPost).where(BlogPost.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")
    post = BlogPost(author_user_id=current_user.id, **data.model_dump())
    if post.is_published and post.published_at is None:
        post.published_at = datetime.now(timezone.utc)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.put("/admin/blog/{post_id}", response_model=BlogPostResponse)
async def update_admin_post(
    post_id: int,
    data: BlogPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    post = await db.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    updates = data.model_dump(exclude_unset=True)
    was_published = post.is_published
    for k, v in updates.items():
        setattr(post, k, v)
    if post.is_published and not was_published and post.published_at is None:
        post.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/admin/blog/{post_id}", status_code=204)
async def delete_admin_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _require_staff(current_user)
    post = await db.get(BlogPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.delete(post)
    await db.commit()
