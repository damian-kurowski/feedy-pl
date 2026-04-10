from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class XmlElementIn(Base):
    __tablename__ = "xml_element_in"
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
    attribute: Mapped[bool] = mapped_column(Boolean, nullable=False)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    parent_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    is_leaf: Mapped[bool] = mapped_column(Boolean, nullable=False)
    element_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)

    feed_in: Mapped["FeedIn"] = relationship("FeedIn", back_populates="xml_elements")
