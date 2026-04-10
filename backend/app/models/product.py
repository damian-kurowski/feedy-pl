from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProductIn(Base):
    __tablename__ = "product_in"
    __table_args__ = {"schema": "data"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    feed_in_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_in.id"), nullable=False
    )
    custom_product: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    product_name: Mapped[str] = mapped_column(String(512), nullable=False)
    product_value: Mapped[dict] = mapped_column(JSONB, nullable=False)

    feed_in: Mapped["FeedIn"] = relationship("FeedIn", back_populates="products")
