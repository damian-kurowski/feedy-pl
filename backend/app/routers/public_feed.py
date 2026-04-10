from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.models.feed_out import FeedOut
from app.models.product import ProductIn
from app.models.product_override import ProductOverride
from app.models.xml_structure import XmlStructureOut
from app.services.feed_generator import generate_allegro_xml, generate_ceneo_xml, generate_gmc_xml, generate_custom_xml, generate_skapiec_xml, generate_domodi_xml
from app.services.override_service import apply_overrides
from app.services.rules_engine import apply_rules

router = APIRouter(tags=["public"])


@router.get("/feed/{feed_uuid}.xml")
async def public_feed(
    feed_uuid: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeedOut).where(FeedOut.link_out == feed_uuid, FeedOut.active == True)  # noqa: E712
    )
    feed_out = result.scalar_one_or_none()
    if not feed_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found",
        )

    # Get products from linked feed_in
    products_result = await db.execute(
        select(ProductIn).where(ProductIn.feed_in_id == feed_out.feed_in_id)
    )
    products = products_result.scalars().all()

    product_dicts = [
        {"id": p.id, "product_value": p.product_value}
        for p in products
    ]

    # Apply per-product overrides
    overrides_result = await db.execute(
        select(ProductOverride).where(ProductOverride.feed_out_id == feed_out.id)
    )
    overrides_list = [
        {"product_in_id": o.product_in_id, "field_overrides": o.field_overrides, "excluded": o.excluded}
        for o in overrides_result.scalars().all()
    ]
    product_dicts = apply_overrides(product_dicts, overrides_list)

    if feed_out.rules:
        product_dicts = apply_rules(product_dicts, feed_out.rules)

    if feed_out.type == "ceneo":
        xml_bytes = generate_ceneo_xml(product_dicts, category_mapping=feed_out.category_mapping)
    elif feed_out.type == "gmc":
        xml_bytes = generate_gmc_xml(product_dicts)
    elif feed_out.type == "allegro":
        xml_bytes = generate_allegro_xml(product_dicts, category_mapping=feed_out.category_mapping)
    elif feed_out.type == "facebook":
        xml_bytes = generate_gmc_xml(product_dicts)
    elif feed_out.type == "skapiec":
        xml_bytes = generate_skapiec_xml(product_dicts, category_mapping=feed_out.category_mapping)
    elif feed_out.type == "domodi":
        xml_bytes = generate_domodi_xml(product_dicts, category_mapping=feed_out.category_mapping)
    else:
        # Custom: load structure and generate
        structure_result = await db.execute(
            select(XmlStructureOut)
            .where(XmlStructureOut.feed_out_id == feed_out.id)
            .order_by(XmlStructureOut.sort_key)
        )
        structure = [
            {
                "path_in": s.path_in,
                "element_name_out": s.element_name_out,
                "is_leaf": s.is_leaf,
                "attribute": s.attribute,
                "sort_key": s.sort_key,
            }
            for s in structure_result.scalars().all()
        ]
        xml_bytes = generate_custom_xml(product_dicts, structure)

    return Response(content=xml_bytes, media_type="application/xml")
