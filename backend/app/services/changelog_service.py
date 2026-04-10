"""Generate changelog by comparing old and new product lists."""

_PRICE_KEYS = ["@price", "g:price", "price"]


def _get_price(pv: dict) -> str | None:
    for key in _PRICE_KEYS:
        val = pv.get(key)
        if val is not None:
            return str(val).strip()
    return None


def generate_changelog(
    old_products: list[dict],
    new_products: list[dict],
) -> list[dict]:
    """Compare old and new product lists, return list of change dicts.

    Each product dict must have ``product_name`` and ``product_value`` keys.

    Returns list of dicts with keys: change_type, product_name, details.
    """
    old_map = {p["product_name"]: p for p in old_products}
    new_map = {p["product_name"]: p for p in new_products}

    changes: list[dict] = []

    # Added products
    for name in new_map:
        if name not in old_map:
            changes.append({
                "change_type": "added",
                "product_name": name,
                "details": {},
            })

    # Removed products
    for name in old_map:
        if name not in new_map:
            changes.append({
                "change_type": "removed",
                "product_name": name,
                "details": {},
            })

    # Modified products
    for name in new_map:
        if name in old_map:
            old_pv = old_map[name].get("product_value", {})
            new_pv = new_map[name].get("product_value", {})

            # Check price change
            old_price = _get_price(old_pv)
            new_price = _get_price(new_pv)
            if old_price and new_price and old_price != new_price:
                changes.append({
                    "change_type": "price_changed",
                    "product_name": name,
                    "details": {"old_price": old_price, "new_price": new_price},
                })
            elif old_pv != new_pv:
                # Find which fields changed
                changed_fields = []
                all_keys = set(list(old_pv.keys()) + list(new_pv.keys()))
                for key in all_keys:
                    if str(old_pv.get(key, "")) != str(new_pv.get(key, "")):
                        changed_fields.append(key)
                if changed_fields:
                    changes.append({
                        "change_type": "modified",
                        "product_name": name,
                        "details": {"changed_fields": changed_fields[:10]},
                    })

    return changes
