from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FeedIn(Base):
    __tablename__ = "feed_in"
    __table_args__ = {"schema": "config"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    record_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetch_status: Mapped[str] = mapped_column(
        String(50), default="pending", server_default="pending"
    )
    refresh_interval: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )  # in minutes: 60, 360, 1440 (1h, 6h, 24h)
    fetch_error: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="feeds_in")
    xml_elements: Mapped[list["XmlElementIn"]] = relationship(
        "XmlElementIn", back_populates="feed_in", cascade="all, delete-orphan"
    )
    products: Mapped[list["ProductIn"]] = relationship(
        "ProductIn", back_populates="feed_in", cascade="all, delete-orphan"
    )
    feeds_out: Mapped[list["FeedOut"]] = relationship(
        "FeedOut", back_populates="feed_in", cascade="all, delete-orphan"
    )
