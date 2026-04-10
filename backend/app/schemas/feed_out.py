from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FeedOutCreate(BaseModel):
    feed_in_id: int
    name: str
    type: str
    template: str | None = None


class FeedOutUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    rules: list[dict] | None = None
    category_mapping: dict | None = None


class FeedOutResponse(BaseModel):
    id: int
    feed_in_id: int
    name: str
    type: str
    template: str | None = None
    active: bool
    link_out: str
    rules: list[dict] | None = None
    category_mapping: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
