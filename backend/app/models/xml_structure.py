from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class XmlStructureOut(Base):
    __tablename__ = "xml_structure_out"
    __table_args__ = {"schema": "data"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    feed_out_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("config.feed_out.id"), nullable=False
    )
    sort_key: Mapped[str] = mapped_column(String(50), nullable=False)
    custom_element: Mapped[bool] = mapped_column(Boolean, nullable=False)
    path_in: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    level_out: Mapped[int] = mapped_column(Integer, nullable=False)
    path_out: Mapped[str] = mapped_column(String(1024), nullable=False)
    parent_path_out: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    element_name_out: Mapped[str] = mapped_column(String(255), nullable=False)
    is_leaf: Mapped[bool] = mapped_column(Boolean, nullable=False)
    attribute: Mapped[bool] = mapped_column(Boolean, nullable=False)

    feed_out: Mapped["FeedOut"] = relationship("FeedOut", back_populates="xml_structures")
