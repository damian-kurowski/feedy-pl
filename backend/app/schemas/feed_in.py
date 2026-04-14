from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FeedInCreate(BaseModel):
    name: str
    source_url: str | None = None


class FeedInUpdate(BaseModel):
    name: Optional[str] = None
    source_url: Optional[str] = None
    record_path: Optional[str] = None
    product_name: Optional[str] = None
    active: Optional[bool] = None
    refresh_interval: Optional[int] = None  # minutes: 60, 360, 1440 or null
    refresh_hours: Optional[str] = None     # cron: "6,18" = run at 06:00 and 18:00
    refresh_weekdays: Optional[str] = None  # cron: "0,1,2,3,4" = Mon-Fri
    webhook_url: Optional[str] = None       # POST after each successful fetch


class FeedInResponse(BaseModel):
    id: int
    name: str
    source_url: str | None = None
    record_path: Optional[str] = None
    product_name: Optional[str] = None
    active: bool
    fetch_status: str
    fetch_error: Optional[str] = None
    last_fetched_at: Optional[datetime] = None
    refresh_interval: Optional[int] = None
    refresh_hours: Optional[str] = None
    refresh_weekdays: Optional[str] = None
    webhook_url: Optional[str] = None
    product_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class XmlElementResponse(BaseModel):
    path: str
    parent_path: Optional[str] = None
    level: int
    element_name: str
    value: Optional[str] = None
    is_leaf: bool
    attribute: bool

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: int
    product_name: str
    product_value: dict
    custom_product: bool

    model_config = {"from_attributes": True}
