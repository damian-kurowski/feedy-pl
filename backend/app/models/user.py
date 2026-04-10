from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    max_products: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_feeds_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_pln: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="plan")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("auth.plans.id"), default=1, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="users")
    feeds_in: Mapped[list["FeedIn"]] = relationship("FeedIn", back_populates="user", cascade="all, delete-orphan")
    feeds_out: Mapped[list["FeedOut"]] = relationship("FeedOut", back_populates="user", cascade="all, delete-orphan")
    org_memberships: Mapped[list["OrgMember"]] = relationship("OrgMember", back_populates="user")
