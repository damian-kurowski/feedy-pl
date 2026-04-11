"""Feed generator service – builds output XML from normalised product data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from lxml import etree

from app.services.templates import ALLEGRO_TEMPLATE, CENEO_TEMPLATE, GMC_TEMPLATE
from app.transformers import format_price, map_availability, strip_html

TRANSFORMS: dict[str, Callable] = {
    "format_price": format_price,
    "map_availability": map_availability,
    "strip_html": strip_html,
}


def _get_value(product_values: dict, source: str) -> str | None:
    """Get value from product_values, trying multiple key variants.

    Product values may come from different feed formats:
    - GMC: keys like "g:id", "title", "g:price", "link"
    - Ceneo: keys like "@id", "name", "@price", "@url"
    - Other: various naming conventions
    """
    # Direct match
    if source in product_values:
        val = product_values[source]
        return str(val) if val is not None else None

    # Try common alternatives (covers GMC, Ceneo, Skapiec/Shoper, Allegro field names)
    alternatives = {
        "g:id": ["@id", "id", "compid"],
        "title": ["name"],
        "link": ["@url", "url"],
        "g:price": ["@price", "price"],
        "g:availability": ["@avail", "avail", "@availability", "availability"],
        "g:product_type": ["cat", "category", "catpath", "catname"],
        "g:google_product_category": ["g:product_type", "cat", "category", "catpath"],
        "g:sale_price": ["@sale_price", "sale_price"],
        "g:shipping_price": ["g:shipping", "shipping_price", "shipping_cost"],
        "description": ["desc", "desclong"],
        "g:image_link": ["image", "img", "photo"],
        "g:brand": ["brand", "vendor", "producent", "producer"],
        "g:gtin": ["ean", "gtin", "code"],
        "g:mpn": ["mpn", "partnr"],
    }

    for alt in alternatives.get(source, []):
        if alt in product_values:
            val = product_values[alt]
            if isinstance(val, dict):
                # Handle nested like imgs: {main: {url: ...}}
                for k, v in val.items():
                    if isinstance(v, dict) and "url" in v:
                        return v["url"]
                    elif isinstance(v, str):
                        return v
            return str(val) if val is not None else None

    return None


def _apply_template(product_values: dict, template: dict[str, dict]) -> dict[str, str | None]:
    """Map source fields through optional transforms, returning output fields."""
    result: dict[str, str | None] = {}
    for output_field, spec in template.items():
        raw = _get_value(product_values, spec["source"])
        transform_name = spec["transform"]
        if transform_name is not None:
            result[output_field] = TRANSFORMS[transform_name](raw)
        else:
            result[output_field] = raw
    return result


def generate_ceneo_xml(products: list[dict], category_mapping: dict | None = None) -> bytes:
    """Generate Ceneo XML feed from a list of product dicts.

    Each product dict must contain a ``product_value`` key holding the field
    values extracted from the source feed.
    """
    root = etree.Element("offers")

    for product in products:
        values = _apply_template(product["product_value"], CENEO_TEMPLATE)

        offer = etree.SubElement(root, "o")
        offer.set("id", values.get("id") or "")
        offer.set("url", values.get("url") or "")
        offer.set("price", values.get("price") or "")
        offer.set("avail", values.get("avail") or "")

        cat = etree.SubElement(offer, "cat")
        cat_val = values.get("cat")
        if category_mapping and cat_val and cat_val in category_mapping:
            cat_val = category_mapping[cat_val]
        cat.text = cat_val

        name = etree.SubElement(offer, "name")
        name.text = values.get("name")

        desc = etree.SubElement(offer, "desc")
        desc.text = values.get("desc")

        imgs = etree.SubElement(offer, "imgs")
        main_img = etree.SubElement(imgs, "main")
        img_url = values.get("img")
        # Handle nested imgs structure from Ceneo source: {"main": {"@url": "..."}}
        if not img_url:
            raw_imgs = product["product_value"].get("imgs")
            if isinstance(raw_imgs, dict):
                main_data = raw_imgs.get("main")
                if isinstance(main_data, dict):
                    img_url = main_data.get("@url")
                elif isinstance(main_data, str):
                    img_url = main_data
        if img_url:
            main_img.set("url", str(img_url))

        # Build attrs only when there is content
        brand = values.get("brand")
        ean = values.get("ean")
        if brand or ean:
            attrs = etree.SubElement(offer, "attrs")
            if brand:
                a_brand = etree.SubElement(attrs, "a")
                a_brand.set("name", "Producent")
                a_brand.text = brand
            if ean:
                a_ean = etree.SubElement(attrs, "a")
                a_ean.set("name", "EAN")
                a_ean.text = ean

    return etree.tostring(
        root,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


# ---------------------------------------------------------------------------
# Allegro XML feed
# ---------------------------------------------------------------------------


def _map_allegro_availability(val: str | None) -> str:
    """Map availability to Allegro format."""
    if not val:
        return "unavailable"
    v = val.strip().lower()
    if v in ("in stock", "1", "available", "in_stock"):
        return "available"
    if v in ("out of stock", "0", "unavailable", "out_of_stock"):
        return "unavailable"
    return "available"


def generate_allegro_xml(products: list[dict], category_mapping: dict | None = None) -> bytes:
    """Generate Allegro-compatible XML feed."""
    root = etree.Element("offers")

    for product in products:
        values = _apply_template(product["product_value"], ALLEGRO_TEMPLATE)

        offer = etree.SubElement(root, "offer")

        for field in ["id", "name", "description", "url", "price", "category", "image", "availability", "brand", "ean", "condition"]:
            val = values.get(field)
            if field == "category" and category_mapping and val and val in category_mapping:
                val = category_mapping[val]
            if field == "availability":
                val = _map_allegro_availability(val)
            if field == "condition" and not val:
                val = "new"
            el = etree.SubElement(offer, field)
            el.text = val or ""

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)


# ---------------------------------------------------------------------------
# Google Merchant Center (Atom) feed
# ---------------------------------------------------------------------------

ATOM_NS = "http://www.w3.org/2005/Atom"
G_NS = "http://base.google.com/ns/1.0"
_GMC_NSMAP = {None: ATOM_NS, "g": G_NS}

# Reverse map: code → GMC text
_AVAIL_REVERSE: dict[str, str] = {
    "1": "in stock",
    "0": "out of stock",
    "99": "preorder",
}


def generate_gmc_xml(products: list[dict]) -> bytes:
    """Generate Google Merchant Center Atom XML feed."""
    root = etree.Element(f"{{{ATOM_NS}}}feed", nsmap=_GMC_NSMAP)

    title_el = etree.SubElement(root, f"{{{ATOM_NS}}}title")
    title_el.text = "Product Feed"

    link_el = etree.SubElement(root, f"{{{ATOM_NS}}}link")
    link_el.set("href", "https://feedy.pl")
    link_el.set("rel", "alternate")
    link_el.set("type", "text/html")

    updated_el = etree.SubElement(root, f"{{{ATOM_NS}}}updated")
    updated_el.text = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for product in products:
        values = _apply_template(product["product_value"], GMC_TEMPLATE)

        entry = etree.SubElement(root, f"{{{ATOM_NS}}}entry")

        # g:id
        gid = etree.SubElement(entry, f"{{{G_NS}}}id")
        gid.text = values.get("g:id")

        # title (Atom namespace)
        t = etree.SubElement(entry, f"{{{ATOM_NS}}}title")
        t.text = values.get("title")

        # description (Atom namespace)
        desc = etree.SubElement(entry, f"{{{ATOM_NS}}}description")
        desc.text = values.get("description")

        # link (Atom namespace, as attribute)
        lnk = etree.SubElement(entry, f"{{{ATOM_NS}}}link")
        url_value = values.get("link") or ""
        lnk.set("href", url_value)
        lnk.set("rel", "alternate")
        lnk.set("type", "text/html")

        # g:image_link
        img = etree.SubElement(entry, f"{{{G_NS}}}image_link")
        img.text = values.get("g:image_link")

        # g:condition – default to "new" when missing
        cond = etree.SubElement(entry, f"{{{G_NS}}}condition")
        cond.text = values.get("g:condition") or "new"

        # g:availability – map back from code to text
        avail = etree.SubElement(entry, f"{{{G_NS}}}availability")
        raw_avail = values.get("g:availability") or ""
        avail.text = _AVAIL_REVERSE.get(raw_avail, raw_avail)

        # g:price – keep currency code as-is (no format_price)
        price = etree.SubElement(entry, f"{{{G_NS}}}price")
        price.text = values.get("g:price")

        # g:brand
        brand_val = values.get("g:brand")
        if brand_val:
            brand = etree.SubElement(entry, f"{{{G_NS}}}brand")
            brand.text = brand_val

        # g:gtin
        gtin_val = values.get("g:gtin")
        if gtin_val:
            gtin = etree.SubElement(entry, f"{{{G_NS}}}gtin")
            gtin.text = gtin_val

        # g:mpn
        mpn_val = values.get("g:mpn")
        if mpn_val:
            mpn = etree.SubElement(entry, f"{{{G_NS}}}mpn")
            mpn.text = mpn_val

        # g:product_type
        ptype_val = values.get("g:product_type")
        if ptype_val:
            ptype = etree.SubElement(entry, f"{{{G_NS}}}product_type")
            ptype.text = ptype_val

        # g:google_product_category – map from product_type/cat if not explicit
        gpc_val = _get_value(product["product_value"], "g:google_product_category")
        if gpc_val:
            gpc = etree.SubElement(entry, f"{{{G_NS}}}google_product_category")
            gpc.text = gpc_val

        # g:sale_price – optional
        sale_price_val = _get_value(product["product_value"], "g:sale_price")
        if sale_price_val:
            sp = etree.SubElement(entry, f"{{{G_NS}}}sale_price")
            sp.text = sale_price_val

        # g:shipping – include shipping info with country PL
        shipping_price_val = _get_value(product["product_value"], "g:shipping_price")
        if shipping_price_val:
            shipping = etree.SubElement(entry, f"{{{G_NS}}}shipping")
            country = etree.SubElement(shipping, f"{{{G_NS}}}country")
            country.text = "PL"
            ship_price = etree.SubElement(shipping, f"{{{G_NS}}}price")
            ship_price.text = shipping_price_val

    return etree.tostring(
        root,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


# ---------------------------------------------------------------------------
# Skapiec XML feed
# ---------------------------------------------------------------------------


def generate_skapiec_xml(products: list[dict], category_mapping: dict | None = None) -> bytes:
    """Generate Skapiec-compatible XML feed."""
    from app.services.templates import SKAPIEC_TEMPLATE

    root = etree.Element("offers")

    for product in products:
        values = _apply_template(product["product_value"], SKAPIEC_TEMPLATE)
        offer = etree.SubElement(root, "offer")

        for field in ["id", "name", "url", "price", "category", "image", "description",
                       "producer", "availability", "ean", "old_price", "shipping"]:
            val = values.get(field)
            if field == "category" and category_mapping and val and val in category_mapping:
                val = category_mapping[val]
            if val:
                el = etree.SubElement(offer, field)
                el.text = val

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)


# ---------------------------------------------------------------------------
# Domodi / Homebook XML feed
# ---------------------------------------------------------------------------


def generate_domodi_xml(products: list[dict], category_mapping: dict | None = None) -> bytes:
    """Generate Domodi/Homebook-compatible XML feed."""
    from app.services.templates import DOMODI_TEMPLATE

    root = etree.Element("offers")

    for product in products:
        values = _apply_template(product["product_value"], DOMODI_TEMPLATE)
        offer = etree.SubElement(root, "offer")

        for field in ["id", "name", "url", "price", "category", "image", "description",
                       "producer", "availability", "ean", "old_price", "shipping",
                       "color", "size", "material", "gender"]:
            val = values.get(field)
            if field == "category" and category_mapping and val and val in category_mapping:
                val = category_mapping[val]
            if val:
                el = etree.SubElement(offer, field)
                el.text = val

    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", pretty_print=True)


# ---------------------------------------------------------------------------
# Custom XML feed (user-defined structure)
# ---------------------------------------------------------------------------


def generate_custom_xml(products: list[dict], structure: list[dict]) -> bytes:
    """Generate XML from user-defined structure mapping.

    *structure* is a list of dicts with keys matching XmlStructureOut columns,
    sorted by ``sort_key``.  Each leaf element maps a ``path_in`` source field
    or ``constant_value`` to an ``element_name_out`` output element.
    Supports ``condition``: "always" or "if_not_empty".
    """
    root = etree.Element("products")

    for product in products:
        pv = product["product_value"]
        item = etree.SubElement(root, "product")

        for row in structure:
            # Skip non-leaf / container rows
            if not row.get("is_leaf", True):
                continue

            # Get value: constant_value takes priority, then source field
            constant = row.get("constant_value")
            source = row.get("path_in")
            if constant:
                value = constant
            elif source:
                value = _get_value(pv, source)
            else:
                continue

            # Apply condition
            condition = row.get("condition", "always")
            if condition == "if_not_empty" and (value is None or value == ""):
                continue
            if value is None:
                continue

            el_name = row.get("element_name_out", source or "field")

            if row.get("attribute", False):
                attr_name = el_name.lstrip("@")
                item.set(attr_name, value)
            else:
                child = etree.SubElement(item, el_name)
                child.text = value

    return etree.tostring(
        root,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )
