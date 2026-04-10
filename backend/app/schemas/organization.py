from pydantic import BaseModel, EmailStr

from app.schemas.auth import PlanResponse


class OrgCreate(BaseModel):
    name: str
    brand_name: str | None = None
    brand_color: str | None = None
    brand_logo_url: str | None = None


class OrgUpdate(BaseModel):
    name: str | None = None
    brand_name: str | None = None
    brand_color: str | None = None
    brand_logo_url: str | None = None
    custom_domain: str | None = None


class OrgResponse(BaseModel):
    id: int
    name: str
    plan: PlanResponse
    brand_name: str | None = None
    brand_color: str | None = None
    brand_logo_url: str | None = None
    custom_domain: str | None = None

    model_config = {"from_attributes": True}


class OrgBrandingResponse(BaseModel):
    brand_name: str
    brand_color: str
    brand_logo_url: str | None = None


class OrgMemberResponse(BaseModel):
    id: int
    user_id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "member"
