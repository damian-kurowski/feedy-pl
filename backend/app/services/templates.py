"""Feed output templates mapping output fields to source fields and transforms."""


def get_ceneo_structure_rows(feed_out_id: int) -> list[dict]:
    """Return xml_structure_out rows for the Ceneo template."""
    return [
        {"feed_out_id": feed_out_id, "sort_key": "1", "custom_element": True, "path_in": None, "level_out": 1, "path_out": "offers", "parent_path_out": None, "element_name_out": "offers", "is_leaf": False, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.1", "custom_element": False, "path_in": "g:id", "level_out": 2, "path_out": "offers/o/@id", "parent_path_out": "offers", "element_name_out": "@id", "is_leaf": True, "attribute": True},
        {"feed_out_id": feed_out_id, "sort_key": "1.2", "custom_element": False, "path_in": "link", "level_out": 2, "path_out": "offers/o/@url", "parent_path_out": "offers", "element_name_out": "@url", "is_leaf": True, "attribute": True},
        {"feed_out_id": feed_out_id, "sort_key": "1.3", "custom_element": False, "path_in": "g:price", "level_out": 2, "path_out": "offers/o/@price", "parent_path_out": "offers", "element_name_out": "@price", "is_leaf": True, "attribute": True},
        {"feed_out_id": feed_out_id, "sort_key": "1.4", "custom_element": False, "path_in": "g:availability", "level_out": 2, "path_out": "offers/o/@avail", "parent_path_out": "offers", "element_name_out": "@avail", "is_leaf": True, "attribute": True},
        {"feed_out_id": feed_out_id, "sort_key": "1.5", "custom_element": False, "path_in": "g:product_type", "level_out": 2, "path_out": "offers/o/cat", "parent_path_out": "offers/o", "element_name_out": "cat", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.6", "custom_element": False, "path_in": "title", "level_out": 2, "path_out": "offers/o/name", "parent_path_out": "offers/o", "element_name_out": "name", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.7", "custom_element": False, "path_in": "description", "level_out": 2, "path_out": "offers/o/desc", "parent_path_out": "offers/o", "element_name_out": "desc", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.8", "custom_element": False, "path_in": "g:image_link", "level_out": 2, "path_out": "offers/o/imgs/main/@url", "parent_path_out": "offers/o", "element_name_out": "img", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.9", "custom_element": False, "path_in": "g:brand", "level_out": 2, "path_out": "offers/o/attrs/Producent", "parent_path_out": "offers/o", "element_name_out": "Producent", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.10", "custom_element": False, "path_in": "g:gtin", "level_out": 2, "path_out": "offers/o/attrs/EAN", "parent_path_out": "offers/o", "element_name_out": "EAN", "is_leaf": True, "attribute": False},
    ]


CENEO_TEMPLATE: dict[str, dict] = {
    "id": {"source": "g:id", "transform": None},
    "url": {"source": "link", "transform": None},
    "price": {"source": "g:price", "transform": "format_price"},
    "avail": {"source": "g:availability", "transform": "map_availability"},
    "cat": {"source": "g:product_type", "transform": None},
    "name": {"source": "title", "transform": None},
    "desc": {"source": "description", "transform": "strip_html"},
    "img": {"source": "g:image_link", "transform": None},
    "brand": {"source": "g:brand", "transform": None},
    "ean": {"source": "g:gtin", "transform": None},
}

GMC_TEMPLATE: dict[str, dict] = {
    field: {"source": field, "transform": None}
    for field in [
        "g:id",
        "title",
        "description",
        "link",
        "g:image_link",
        "g:condition",
        "g:availability",
        "g:price",
        "g:brand",
        "g:gtin",
        "g:mpn",
        "g:product_type",
    ]
}

ALLEGRO_TEMPLATE: dict[str, dict] = {
    "id": {"source": "g:id", "transform": None},
    "name": {"source": "title", "transform": None},
    "description": {"source": "description", "transform": "strip_html"},
    "url": {"source": "link", "transform": None},
    "price": {"source": "g:price", "transform": "format_price"},
    "category": {"source": "g:product_type", "transform": None},
    "image": {"source": "g:image_link", "transform": None},
    "availability": {"source": "g:availability", "transform": None},
    "brand": {"source": "g:brand", "transform": None},
    "ean": {"source": "g:gtin", "transform": None},
    "condition": {"source": "g:condition", "transform": None},
}


def get_allegro_structure_rows(feed_out_id: int) -> list[dict]:
    """Return xml_structure_out rows for the Allegro template."""
    return [
        {"feed_out_id": feed_out_id, "sort_key": "1", "custom_element": True, "path_in": None, "level_out": 1, "path_out": "offers", "parent_path_out": None, "element_name_out": "offers", "is_leaf": False, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.1", "custom_element": False, "path_in": "g:id", "level_out": 2, "path_out": "offers/offer/id", "parent_path_out": "offers/offer", "element_name_out": "id", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.2", "custom_element": False, "path_in": "title", "level_out": 2, "path_out": "offers/offer/name", "parent_path_out": "offers/offer", "element_name_out": "name", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.3", "custom_element": False, "path_in": "description", "level_out": 2, "path_out": "offers/offer/description", "parent_path_out": "offers/offer", "element_name_out": "description", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.4", "custom_element": False, "path_in": "link", "level_out": 2, "path_out": "offers/offer/url", "parent_path_out": "offers/offer", "element_name_out": "url", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.5", "custom_element": False, "path_in": "g:price", "level_out": 2, "path_out": "offers/offer/price", "parent_path_out": "offers/offer", "element_name_out": "price", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.6", "custom_element": False, "path_in": "g:product_type", "level_out": 2, "path_out": "offers/offer/category", "parent_path_out": "offers/offer", "element_name_out": "category", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.7", "custom_element": False, "path_in": "g:image_link", "level_out": 2, "path_out": "offers/offer/image", "parent_path_out": "offers/offer", "element_name_out": "image", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.8", "custom_element": False, "path_in": "g:availability", "level_out": 2, "path_out": "offers/offer/availability", "parent_path_out": "offers/offer", "element_name_out": "availability", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.9", "custom_element": False, "path_in": "g:brand", "level_out": 2, "path_out": "offers/offer/brand", "parent_path_out": "offers/offer", "element_name_out": "brand", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.10", "custom_element": False, "path_in": "g:gtin", "level_out": 2, "path_out": "offers/offer/ean", "parent_path_out": "offers/offer", "element_name_out": "ean", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.11", "custom_element": False, "path_in": "g:condition", "level_out": 2, "path_out": "offers/offer/condition", "parent_path_out": "offers/offer", "element_name_out": "condition", "is_leaf": True, "attribute": False},
    ]


SKAPIEC_TEMPLATE: dict[str, dict] = {
    "id": {"source": "g:id", "transform": None},
    "name": {"source": "title", "transform": None},
    "url": {"source": "link", "transform": None},
    "price": {"source": "g:price", "transform": "format_price"},
    "category": {"source": "g:product_type", "transform": None},
    "image": {"source": "g:image_link", "transform": None},
    "description": {"source": "description", "transform": "strip_html"},
    "producer": {"source": "g:brand", "transform": None},
    "availability": {"source": "g:availability", "transform": "map_availability"},
    "ean": {"source": "g:gtin", "transform": None},
    "old_price": {"source": "g:sale_price", "transform": None},
    "shipping": {"source": "g:shipping_price", "transform": None},
}

DOMODI_TEMPLATE: dict[str, dict] = {
    **SKAPIEC_TEMPLATE,
    "color": {"source": "color", "transform": None},
    "size": {"source": "size", "transform": None},
    "material": {"source": "material", "transform": None},
    "gender": {"source": "gender", "transform": None},
}


def get_skapiec_structure_rows(feed_out_id: int) -> list[dict]:
    """Return xml_structure_out rows for the Skapiec template."""
    return [
        {"feed_out_id": feed_out_id, "sort_key": "1", "custom_element": True, "path_in": None, "level_out": 1, "path_out": "offers", "parent_path_out": None, "element_name_out": "offers", "is_leaf": False, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.1", "custom_element": False, "path_in": "g:id", "level_out": 2, "path_out": "offers/offer/id", "parent_path_out": "offers/offer", "element_name_out": "id", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.2", "custom_element": False, "path_in": "title", "level_out": 2, "path_out": "offers/offer/name", "parent_path_out": "offers/offer", "element_name_out": "name", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.3", "custom_element": False, "path_in": "link", "level_out": 2, "path_out": "offers/offer/url", "parent_path_out": "offers/offer", "element_name_out": "url", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.4", "custom_element": False, "path_in": "g:price", "level_out": 2, "path_out": "offers/offer/price", "parent_path_out": "offers/offer", "element_name_out": "price", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.5", "custom_element": False, "path_in": "g:product_type", "level_out": 2, "path_out": "offers/offer/category", "parent_path_out": "offers/offer", "element_name_out": "category", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.6", "custom_element": False, "path_in": "g:image_link", "level_out": 2, "path_out": "offers/offer/image", "parent_path_out": "offers/offer", "element_name_out": "image", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.7", "custom_element": False, "path_in": "description", "level_out": 2, "path_out": "offers/offer/description", "parent_path_out": "offers/offer", "element_name_out": "description", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.8", "custom_element": False, "path_in": "g:brand", "level_out": 2, "path_out": "offers/offer/producer", "parent_path_out": "offers/offer", "element_name_out": "producer", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.9", "custom_element": False, "path_in": "g:availability", "level_out": 2, "path_out": "offers/offer/availability", "parent_path_out": "offers/offer", "element_name_out": "availability", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.10", "custom_element": False, "path_in": "g:gtin", "level_out": 2, "path_out": "offers/offer/ean", "parent_path_out": "offers/offer", "element_name_out": "ean", "is_leaf": True, "attribute": False},
    ]


def get_domodi_structure_rows(feed_out_id: int) -> list[dict]:
    """Return xml_structure_out rows for the Domodi template."""
    rows = get_skapiec_structure_rows(feed_out_id)
    rows.extend([
        {"feed_out_id": feed_out_id, "sort_key": "1.11", "custom_element": False, "path_in": "color", "level_out": 2, "path_out": "offers/offer/color", "parent_path_out": "offers/offer", "element_name_out": "color", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.12", "custom_element": False, "path_in": "size", "level_out": 2, "path_out": "offers/offer/size", "parent_path_out": "offers/offer", "element_name_out": "size", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.13", "custom_element": False, "path_in": "material", "level_out": 2, "path_out": "offers/offer/material", "parent_path_out": "offers/offer", "element_name_out": "material", "is_leaf": True, "attribute": False},
        {"feed_out_id": feed_out_id, "sort_key": "1.14", "custom_element": False, "path_in": "gender", "level_out": 2, "path_out": "offers/offer/gender", "parent_path_out": "offers/offer", "element_name_out": "gender", "is_leaf": True, "attribute": False},
    ])
    return rows
