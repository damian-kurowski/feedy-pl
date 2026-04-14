from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CompetitorPriceSnapshot(Base):
    """One scraped snapshot of competitor offers for a single product on Ceneo.

    We snapshot per (product_in_id, scraped_at) so we can chart trends over
    time. The latest snapshot for each product is served to the UI.
    """

    __tablename__ = "competitor_price_snapshots"
    __table_args__ = {"schema": "data"}

    id: Mapped[int] = mapped_column(primary_key=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    product_in_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("data.product_in.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ean: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    # Our price at time of scrape
    our_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Cheapest competitor (excluding our own offer)
    lowest_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    lowest_seller: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 1-based position of our offer in Ceneo listing (None if not found)
    our_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_offers: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Full snapshot for debugging / advanced analytics
    # Shape: [{"seller": "...", "price": 99.99, "url": "..."}, ...]
    offers: Mapped[list | None] = mapped_column(JSONB, nullable=True)
