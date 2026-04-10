"""Apply per-product overrides to product list."""


def apply_overrides(
    products: list[dict], overrides: list[dict]
) -> list[dict]:
    """Merge field_overrides into products and exclude marked products.

    *products* — list of dicts with ``id`` and ``product_value`` keys.
    *overrides* — list of dicts with ``product_in_id``, ``field_overrides``, ``excluded``.

    Returns a new list (does not mutate originals).
    """
    if not overrides:
        return products

    override_map: dict[int, dict] = {o["product_in_id"]: o for o in overrides}
    result: list[dict] = []

    for product in products:
        pid = product.get("id")
        ov = override_map.get(pid)

        if ov and ov.get("excluded"):
            continue

        if ov and ov.get("field_overrides"):
            merged_pv = {**product["product_value"], **ov["field_overrides"]}
            result.append({**product, "product_value": merged_pv})
        else:
            result.append(product)

    return result
