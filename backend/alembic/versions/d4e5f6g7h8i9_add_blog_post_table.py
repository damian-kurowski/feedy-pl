"""add blog_post table

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-04-14

"""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6g7h8i9"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blog_post",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("html", sa.Text, nullable=False),
        sa.Column("is_published", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_title", sa.String(255), nullable=True),
        sa.Column("meta_description", sa.String(320), nullable=True),
        sa.Column("is_indexable", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("is_followable", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("hero_image_path", sa.String(255), nullable=True),
        sa.Column("hero_image_alt", sa.String(255), nullable=True),
        sa.Column("og_image_path", sa.String(255), nullable=True),
        sa.Column("author_user_id", sa.BigInteger, nullable=True),
        sa.Column("reading_minutes", sa.Integer, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("excerpt", sa.String(500), nullable=True),
        schema="config",
    )


def downgrade() -> None:
    op.drop_table("blog_post", schema="config")
