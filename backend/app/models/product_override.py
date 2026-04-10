from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductOverride(Base):
    __tablename__ = "product_override"
    __table_args__ = (
        UniqueConstraint("feed_out_id", "product_in_id"),
        {"schema": "data"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    feed_out_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_out.id", ondelete="CASCADE"), nullable=False
    )
    product_in_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("data.product_in.id", ondelete="CASCADE"), nullable=False
    )
    field_overrides: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    excluded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
