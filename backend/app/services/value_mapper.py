"""Apply value maps to product fields during feed generation."""


def apply_value_maps(
    products: list[dict],
    field_maps: dict[str, dict],
) -> list[dict]:
    """Apply value mappings to product fields.

    *field_maps* maps field names to mapping dicts: {"field_name": {"old_val": "new_val", ...}}
    """
    if not field_maps:
        return products

    for product in products:
        pv = product.get("product_value", {})
        for field_name, mapping in field_maps.items():
            if field_name in pv:
                val = str(pv[field_name]).strip()
                if val in mapping:
                    pv[field_name] = mapping[val]

    return products
