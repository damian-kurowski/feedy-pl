from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FeedOut(Base):
    __tablename__ = "feed_out"
    __table_args__ = {"schema": "config"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.users.id"), nullable=False)
    feed_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_in.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    template: Mapped[str | None] = mapped_column(String(50), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    link_out: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    rules: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=None)
    category_mapping: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    field_maps: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)

    user: Mapped["User"] = relationship("User", back_populates="feeds_out")
    feed_in: Mapped["FeedIn"] = relationship("FeedIn", back_populates="feeds_out")
    xml_structures: Mapped[list["XmlStructureOut"]] = relationship(
        "XmlStructureOut", back_populates="feed_out", cascade="all, delete-orphan"
    )
