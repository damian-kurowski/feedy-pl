from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LandingPage(Base):
    __tablename__ = "landing_page"
    __table_args__ = {"schema": "config"}

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.users.id"), nullable=False, index=True)

    slug: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    full_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    hero_image: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gallery: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    price: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_negotiable: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    cta_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cta_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(320), nullable=True)
    is_indexable: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    is_followable: Mapped[bool] = mapped_column(Boolean, server_default="true", default=True)
    is_published: Mapped[bool] = mapped_column(Boolean, server_default="false", default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
