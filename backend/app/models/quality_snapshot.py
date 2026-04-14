from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedQualitySnapshot(Base):
    __tablename__ = "feed_quality_snapshots"
    __table_args__ = {"schema": "data"}

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    feed_out_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_out.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quality_score: Mapped[int] = mapped_column(Integer, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    products_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
