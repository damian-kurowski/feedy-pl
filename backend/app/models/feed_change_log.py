from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FeedChangeLog(Base):
    __tablename__ = "feed_change_log"
    __table_args__ = {"schema": "data"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    feed_in_id: Mapped[int] = mapped_column(Integer, ForeignKey("config.feed_in.id", ondelete="CASCADE"), nullable=False)
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(512))
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
