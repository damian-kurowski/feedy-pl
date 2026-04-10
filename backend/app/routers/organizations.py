from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.organization import OrgMember, Organization
from app.models.user import User
from app.schemas.organization import (
    InviteRequest,
    OrgBrandingResponse,
    OrgCreate,
    OrgMemberResponse,
    OrgResponse,
    OrgUpdate,
)

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.post("", response_model=OrgResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    data: OrgCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = Organization(
        name=data.name,
        plan_id=current_user.plan_id,
        brand_name=data.brand_name,
        brand_color=data.brand_color,
        brand_logo_url=data.brand_logo_url,
    )
    db.add(org)
    await db.flush()

    member = OrgMember(organization_id=org.id, user_id=current_user.id, role="owner")
    db.add(member)
    await db.commit()

    result = await db.execute(
        select(Organization).options(selectinload(Organization.plan)).where(Organization.id == org.id)
    )
    return result.scalar_one()


@router.get("", response_model=list[OrgResponse])
async def list_orgs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization)
        .join(OrgMember, OrgMember.organization_id == Organization.id)
        .options(selectinload(Organization.plan))
        .where(OrgMember.user_id == current_user.id)
    )
    return result.scalars().all()


@router.put("/{org_id}", response_model=OrgResponse)
async def update_org(
    org_id: int,
    data: OrgUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check user is owner or admin
    role_result = await db.execute(
        select(OrgMember.role).where(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == current_user.id,
        )
    )
    role = role_result.scalar_one_or_none()
    if role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    result = await db.execute(
        select(Organization).options(selectinload(Organization.plan)).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)

    await db.commit()
    await db.refresh(org)
    return org


@router.get("/{org_id}/branding", response_model=OrgBrandingResponse)
async def get_branding(
    org_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint -- no auth needed. Returns branding for an org."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrgBrandingResponse(
        brand_name=org.brand_name or "Feedy",
        brand_color=org.brand_color or "#4F46E5",
        brand_logo_url=org.brand_logo_url,
    )


async def _get_member_role(db: AsyncSession, org_id: int, user_id: int) -> str | None:
    result = await db.execute(
        select(OrgMember.role).where(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


@router.get("/{org_id}/members", response_model=list[OrgMemberResponse])
async def list_members(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await _get_member_role(db, org_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    result = await db.execute(
        select(OrgMember)
        .options(selectinload(OrgMember.user))
        .where(OrgMember.organization_id == org_id)
    )
    members = result.scalars().all()
    return [
        OrgMemberResponse(id=m.id, user_id=m.user_id, email=m.user.email, role=m.role)
        for m in members
    ]


@router.post("/{org_id}/invite", response_model=OrgMemberResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: int,
    data: InviteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await _get_member_role(db, org_id, current_user.id)
    if role not in ("owner", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    # Find the user by email
    result = await db.execute(select(User).where(User.email == data.email))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if already a member
    existing = await db.execute(
        select(OrgMember).where(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == target_user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")

    member = OrgMember(organization_id=org_id, user_id=target_user.id, role=data.role)
    db.add(member)
    await db.commit()
    await db.refresh(member)

    return OrgMemberResponse(
        id=member.id, user_id=member.user_id, email=target_user.email, role=member.role
    )


@router.delete("/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: int,
    member_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await _get_member_role(db, org_id, current_user.id)
    if role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can remove members")

    result = await db.execute(
        select(OrgMember).where(OrgMember.id == member_id, OrgMember.organization_id == org_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if member.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself")

    await db.delete(member)
    await db.commit()
