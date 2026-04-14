from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BlogPost(Base):
    __tablename__ = "blog_post"
    __table_args__ = {"schema": "config"}

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    html: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(320), nullable=True)
    is_indexable: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True, nullable=False)
    is_followable: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True, nullable=False)
    hero_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hero_image_alt: Mapped[str | None] = mapped_column(String(255), nullable=True)
    og_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_user_id: Mapped[int | None] = mapped_column(nullable=True)
    reading_minutes: Mapped[int | None] = mapped_column(nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(String(500), nullable=True)
