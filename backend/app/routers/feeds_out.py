import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.feed_in import FeedIn
from app.models.feed_out import FeedOut
from app.models.product import ProductIn
from app.models.user import User
from app.models.xml_structure import XmlStructureOut
from app.schemas.feed_out import FeedOutCreate, FeedOutResponse, FeedOutUpdate
from app.schemas.xml_structure import StructureElementIn, StructureElementResponse
from app.services.ceneo_categories import get_all_categories, suggest_ceneo_category
from app.services.google_taxonomy import search_google_categories
from app.services.templates import get_skapiec_structure_rows, get_domodi_structure_rows
from app.services.feed_generator import _get_value, generate_ceneo_xml, generate_gmc_xml
from app.services.validators import validate_feed
from app.services.title_optimizer import optimize_titles_bulk
from app.models.product_override import ProductOverride
from app.schemas.product_override import ProductOverrideUpsert, ProductWithOverrideResponse
from app.services.override_service import apply_overrides as apply_product_overrides
from app.services.platform_info import get_platform_info, get_all_platforms

router = APIRouter(prefix="/api/feeds-out", tags=["feeds-out"])


@router.get("/ceneo-categories")
async def list_ceneo_categories(
    q: str = "",
    user: User = Depends(get_current_user),
):
    if q:
        return {"categories": suggest_ceneo_category(q, limit=10)}
    return {"categories": get_all_categories()}


@router.get("/google-categories")
async def list_google_categories(
    q: str = "",
    limit: int = 10,
    user: User = Depends(get_current_user),
):
    return {"categories": search_google_categories(q, limit=limit)}


async def _get_user_feed_out(db: AsyncSession, feed_out_id: int, user_id: int) -> FeedOut:
    result = await db.execute(
        select(FeedOut).where(FeedOut.id == feed_out_id, FeedOut.user_id == user_id)
    )
    feed_out = result.scalar_one_or_none()
    if not feed_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed out not found",
        )
    return feed_out


@router.get("", response_model=list[FeedOutResponse])
async def list_feeds_out(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeedOut)
        .where(FeedOut.user_id == current_user.id)
        .order_by(FeedOut.created_at.desc())
    )
    return result.scalars().all()


@router.get("/platforms")
async def list_platforms(user: User = Depends(get_current_user)):
    return get_all_platforms()


@router.get("/platform-info/{platform}")
async def platform_info_endpoint(platform: str, user: User = Depends(get_current_user)):
    info = get_platform_info(platform)
    if not info:
        raise HTTPException(status_code=404, detail="Unknown platform")
    return info


@router.post("", response_model=FeedOutResponse, status_code=status.HTTP_201_CREATED)
async def create_feed_out(
    data: FeedOutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check feed_in belongs to user
    result = await db.execute(
        select(FeedIn).where(FeedIn.id == data.feed_in_id, FeedIn.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed in not found",
        )

    # Plan limit check disabled for development
    # plan = current_user.plan
    # if plan and plan.max_feeds_out is not None:
    #     count_result = await db.execute(
    #         select(func.count()).select_from(FeedOut).where(FeedOut.user_id == current_user.id)
    #     )
    #     current_count = count_result.scalar()
    #     if current_count >= plan.max_feeds_out:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail=f"Plan '{plan.name}' allows max {plan.max_feeds_out} output feeds. Upgrade to add more.",
    #         )

    feed_out = FeedOut(
        user_id=current_user.id,
        feed_in_id=data.feed_in_id,
        name=data.name,
        type=data.type,
        template=data.template,
        link_out=str(_uuid.uuid4()),
    )
    db.add(feed_out)
    await db.commit()
    await db.refresh(feed_out)

    # Auto-populate structure from template
    if data.template == "ceneo":
        from app.services.templates import get_ceneo_structure_rows
        for row in get_ceneo_structure_rows(feed_out.id):
            db.add(XmlStructureOut(**row))
        await db.commit()
    elif data.template == "allegro":
        from app.services.templates import get_allegro_structure_rows
        for row in get_allegro_structure_rows(feed_out.id):
            db.add(XmlStructureOut(**row))
        await db.commit()
    elif data.template == "skapiec":
        for row in get_skapiec_structure_rows(feed_out.id):
            db.add(XmlStructureOut(**row))
        await db.commit()
    elif data.template == "domodi":
        for row in get_domodi_structure_rows(feed_out.id):
            db.add(XmlStructureOut(**row))
        await db.commit()

    return feed_out


@router.get("/{feed_out_id}", response_model=FeedOutResponse)
async def get_feed_out(
    feed_out_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _get_user_feed_out(db, feed_out_id, current_user.id)


@router.put("/{feed_out_id}", response_model=FeedOutResponse)
async def update_feed_out(
    feed_out_id: int,
    data: FeedOutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, current_user.id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(feed_out, key, value)
    await db.commit()
    await db.refresh(feed_out)
    return feed_out


@router.delete("/{feed_out_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed_out(
    feed_out_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, current_user.id)
    await db.delete(feed_out)
    await db.commit()


@router.get("/{feed_out_id}/products")
async def list_feed_products(
    feed_out_id: int,
    search: str = "",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    query = select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    if search:
        query = query.where(ProductIn.product_name.ilike(f"%{search}%"))
    products_result = await db.execute(query.limit(100))
    products = products_result.scalars().all()

    overrides_result = await db.execute(
        select(ProductOverride).where(ProductOverride.feed_out_id == feed_out_id)
    )
    override_map = {o.product_in_id: o for o in overrides_result.scalars().all()}

    result = []
    for p in products:
        ov = override_map.get(p.id)
        if ov and ov.excluded:
            status = "excluded"
        elif ov and ov.field_overrides:
            status = "modified"
        else:
            status = "original"

        merged_pv = p.product_value
        if ov and ov.field_overrides:
            merged_pv = {**p.product_value, **ov.field_overrides}

        result.append({
            "id": p.id,
            "product_name": p.product_name,
            "product_value": merged_pv,
            "override": {"field_overrides": ov.field_overrides, "excluded": ov.excluded} if ov else None,
            "status": status,
        })
    return result


@router.put("/{feed_out_id}/products/{product_id}/override")
async def upsert_override(
    feed_out_id: int,
    product_id: int,
    data: ProductOverrideUpsert,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    product_result = await db.execute(
        select(ProductIn).where(
            ProductIn.id == product_id,
            ProductIn.feed_in_id == feed_out.feed_in_id,
        )
    )
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found in this feed")

    existing = await db.execute(
        select(ProductOverride).where(
            ProductOverride.feed_out_id == feed_out_id,
            ProductOverride.product_in_id == product_id,
        )
    )
    override = existing.scalar_one_or_none()
    if override:
        override.field_overrides = data.field_overrides
        override.excluded = data.excluded
    else:
        override = ProductOverride(
            feed_out_id=feed_out_id,
            product_in_id=product_id,
            field_overrides=data.field_overrides,
            excluded=data.excluded,
        )
        db.add(override)
    await db.commit()
    return {"status": "ok", "field_overrides": data.field_overrides, "excluded": data.excluded}


@router.delete("/{feed_out_id}/products/{product_id}/override", status_code=204)
async def delete_override(
    feed_out_id: int,
    product_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed_out(db, feed_out_id, user.id)
    result = await db.execute(
        select(ProductOverride).where(
            ProductOverride.feed_out_id == feed_out_id,
            ProductOverride.product_in_id == product_id,
        )
    )
    override = result.scalar_one_or_none()
    if override:
        await db.delete(override)
        await db.commit()


@router.get("/{feed_out_id}/validate")
async def validate_feed_endpoint(
    feed_out_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    # Get products
    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    )
    products = [{"id": p.id, "product_value": p.product_value} for p in products_result.scalars().all()]

    # Apply per-product overrides
    overrides_result = await db.execute(
        select(ProductOverride).where(ProductOverride.feed_out_id == feed_out.id)
    )
    overrides = [
        {"product_in_id": o.product_in_id, "field_overrides": o.field_overrides, "excluded": o.excluded}
        for o in overrides_result.scalars().all()
    ]
    products = apply_product_overrides(products, overrides)

    # Apply rules if any
    if feed_out.rules:
        from app.services.rules_engine import apply_rules
        products = apply_rules(products, feed_out.rules)

    result = validate_feed(feed_out.type, products)

    return {
        "platform": result.platform,
        "total_products": result.total_products,
        "quality_score": result.quality_score,
        "quality_label": result.quality_label,
        "quality_breakdown": result.quality_breakdown,
        "summary": {
            "errors": sum(1 for i in result.issues if i.level == "error"),
            "warnings": sum(1 for i in result.issues if i.level == "warning"),
            "info": sum(1 for i in result.issues if i.level == "info"),
        },
        "field_coverage": [
            {
                "field": c.field,
                "required": c.required,
                "filled": c.filled,
                "total": c.total,
                "percent": c.percent,
            }
            for c in result.field_coverage
        ],
        "issues": [
            {
                "level": i.level,
                "field": i.field,
                "message": i.message,
                "product_id": i.product_id,
                "product_name": i.product_name,
                "rule": i.rule,
            }
            for i in result.issues[:100]
        ],
    }


@router.post("/{feed_out_id}/optimize-titles")
async def preview_optimized_titles(
    feed_out_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Preview title optimization for a feed's products."""
    feed_out = await _get_user_feed_out(db, feed_out_id, user.id)

    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id).limit(10)
    )
    products = [{"product_value": p.product_value} for p in products_result.scalars().all()]

    optimized = optimize_titles_bulk(products)

    # Return comparison
    comparisons = []
    for orig, opt in zip(products, optimized):
        orig_title = _get_value(orig["product_value"], "title") or ""
        opt_title = _get_value(opt["product_value"], "title") or ""
        comparisons.append({
            "original": orig_title,
            "optimized": opt_title,
            "changed": orig_title != opt_title,
        })

    return {"comparisons": comparisons}


@router.get("/{feed_out_id}/structure", response_model=list[StructureElementResponse])
async def list_structure(
    feed_out_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed_out(db, feed_out_id, current_user.id)
    result = await db.execute(
        select(XmlStructureOut)
        .where(XmlStructureOut.feed_out_id == feed_out_id)
        .order_by(XmlStructureOut.sort_key)
    )
    return result.scalars().all()


@router.put("/{feed_out_id}/structure", response_model=list[StructureElementResponse])
async def replace_structure(
    feed_out_id: int,
    elements: list[StructureElementIn],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_feed_out(db, feed_out_id, current_user.id)

    # Delete all existing
    await db.execute(
        delete(XmlStructureOut).where(XmlStructureOut.feed_out_id == feed_out_id)
    )

    # Insert new
    new_elements = []
    for elem in elements:
        structure = XmlStructureOut(
            feed_out_id=feed_out_id,
            sort_key=elem.sort_key,
            custom_element=elem.custom_element,
            path_in=elem.path_in,
            level_out=elem.level_out,
            path_out=elem.path_out,
            parent_path_out=elem.parent_path_out,
            element_name_out=elem.element_name_out,
            is_leaf=elem.is_leaf,
            attribute=elem.attribute,
        )
        db.add(structure)
        new_elements.append(structure)

    await db.commit()
    for elem in new_elements:
        await db.refresh(elem)

    return new_elements
