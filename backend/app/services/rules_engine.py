"""Rules engine for filtering and modifying products before XML generation."""

import re

# Alternative field names across different feed sources (GMC, Ceneo, Skapiec).
_FIELD_ALTERNATIVES = {
    "g:product_type": ["cat", "category", "catpath", "@cat"],
    "title": ["name", "g:title"],
    "g:price": ["@price", "price"],
    "g:brand": ["brand", "vendor", "producent"],
    "description": ["desc", "g:description"],
}

_IMAGE_FIELDS = ["g:image_link", "image", "img", "imgurl", "imgs"]
_PRICE_FIELDS = ["g:price", "@price", "price"]


def _get_field_value(pv: dict, field: str) -> str | None:
    """Get field value, trying common alternatives."""
    if field in pv:
        val = pv[field]
        return str(val) if val is not None else None

    for alt in _FIELD_ALTERNATIVES.get(field, []):
        if alt in pv:
            val = pv[alt]
            return str(val) if val is not None else None
    return None


def _find_actual_key(pv: dict, field: str) -> str | None:
    """Find the actual key present in pv for a logical field name."""
    if field in pv:
        return field
    for alt in _FIELD_ALTERNATIVES.get(field, []):
        if alt in pv:
            return alt
    return None


def _has_image(pv: dict) -> bool:
    """Check if any image field has a non-empty value."""
    for field in _IMAGE_FIELDS:
        val = pv.get(field)
        if val is None:
            continue
        # Ceneo stores images as nested dict like {"main": {"@url": "..."}}
        if isinstance(val, dict):
            if val:  # non-empty dict counts as having an image
                return True
        elif val:  # non-empty string
            return True
    return False


def _has_price(pv: dict) -> bool:
    """Check if any price field has a non-empty, non-zero value."""
    for field in _PRICE_FIELDS:
        val = pv.get(field)
        if val is not None and str(val).strip() and str(val).strip() != "0":
            return True
    return False


def _extract_number(s: str) -> float:
    """Extract the first numeric value from a string (e.g. '150 PLN' -> 150.0)."""
    match = re.search(r"[\d.]+", s or "")
    return float(match.group()) if match else 0.0


def _evaluate_condition(pv: dict, condition: dict) -> bool:
    """Evaluate a condition against a product's values."""
    value = _get_field_value(pv, condition["field"])
    operator = condition["operator"]
    compare = condition.get("value", "")

    if operator == "eq":
        return str(value or "") == compare
    if operator == "neq":
        return str(value or "") != compare
    if operator == "gt":
        try:
            return _extract_number(value or "") > float(compare)
        except (ValueError, TypeError):
            return False
    if operator == "lt":
        try:
            return _extract_number(value or "") < float(compare)
        except (ValueError, TypeError):
            return False
    if operator == "contains":
        return compare.lower() in (value or "").lower()
    if operator == "not_contains":
        return compare.lower() not in (value or "").lower()
    if operator == "is_empty":
        return not value or value.strip() == ""
    if operator == "is_not_empty":
        return bool(value and value.strip())
    return False


def apply_rules(products: list[dict], rules: list[dict] | None) -> list[dict]:
    """Apply filtering/modification rules to products.

    Rule format:
    {
        "type": "filter_exclude" | "filter_include" | "modify_prefix" | "modify_replace"
               | "filter_no_image" | "filter_no_price" | "title_template" | "conditional"
               | "regex_replace" | "field_merge" | "set_value" | "copy_field"
               | "optimize_titles",
        "field": "field_name",  # which product_value field to check
        "value": "match_value",  # for filter rules
        "new_value": "replacement",  # for modify_replace rules
    }
    """
    if not rules:
        return products

    result = products
    for rule in rules:
        result = _apply_rule(result, rule)
    return result


def _apply_rule(products: list[dict], rule: dict) -> list[dict]:
    rule_type = rule.get("type", "")

    if rule_type == "filter_exclude":
        return _filter_exclude(products, rule)
    elif rule_type == "filter_include":
        return _filter_include(products, rule)
    elif rule_type == "filter_no_image":
        return _filter_no_image(products)
    elif rule_type == "filter_no_price":
        return _filter_no_price(products)
    elif rule_type == "modify_prefix":
        return _modify_prefix(products, rule)
    elif rule_type == "modify_replace":
        return _modify_replace(products, rule)
    elif rule_type == "title_template":
        return _title_template(products, rule)
    elif rule_type == "conditional":
        return _conditional(products, rule)
    elif rule_type == "regex_replace":
        return _regex_replace(products, rule)
    elif rule_type == "field_merge":
        return _field_merge(products, rule)
    elif rule_type == "set_value":
        return _set_value(products, rule)
    elif rule_type == "copy_field":
        return _copy_field(products, rule)
    elif rule_type == "optimize_titles":
        from app.services.title_optimizer import optimize_titles_bulk
        return optimize_titles_bulk(products)
    elif rule_type == "description_template":
        return _description_template(products, rule)

    return products


def _filter_exclude(products: list[dict], rule: dict) -> list[dict]:
    """Remove products where product_value[field] contains value (case-insensitive)."""
    field = rule.get("field", "")
    value = rule.get("value", "").lower()
    return [
        p for p in products
        if value not in (_get_field_value(p.get("product_value", {}), field) or "").lower()
    ]


def _filter_include(products: list[dict], rule: dict) -> list[dict]:
    """Keep ONLY products where product_value[field] contains value (case-insensitive)."""
    field = rule.get("field", "")
    value = rule.get("value", "").lower()
    return [
        p for p in products
        if value in (_get_field_value(p.get("product_value", {}), field) or "").lower()
    ]


def _filter_no_image(products: list[dict]) -> list[dict]:
    """Remove products that have no image across all known image fields."""
    return [p for p in products if _has_image(p.get("product_value", {}))]


def _filter_no_price(products: list[dict]) -> list[dict]:
    """Remove products where price is None/empty/0 across all known price fields."""
    return [p for p in products if _has_price(p.get("product_value", {}))]


def _modify_prefix(products: list[dict], rule: dict) -> list[dict]:
    """Add prefix to product_value[field] for all products."""
    field = rule.get("field", "")
    prefix = rule.get("value", "")
    for p in products:
        pv = p.get("product_value", {})
        actual_key = _find_actual_key(pv, field)
        if actual_key is not None and pv[actual_key] is not None:
            pv[actual_key] = prefix + str(pv[actual_key])
    return products


def _modify_replace(products: list[dict], rule: dict) -> list[dict]:
    """Replace text in product_value[field] for all products."""
    field = rule.get("field", "")
    old_value = rule.get("value", "")
    new_value = rule.get("new_value", "")
    for p in products:
        pv = p.get("product_value", {})
        actual_key = _find_actual_key(pv, field)
        if actual_key is not None and pv[actual_key] is not None:
            pv[actual_key] = str(pv[actual_key]).replace(old_value, new_value)
    return products


def _title_template(products: list[dict], rule: dict) -> list[dict]:
    """Replace field value with a template. Placeholders {field_name} are resolved."""
    field = rule.get("field", "")
    template = rule.get("template", "")
    for p in products:
        pv = p.get("product_value", {})
        actual_key = _find_actual_key(pv, field)
        # If the field doesn't exist yet, use the logical field name as key.
        if actual_key is None:
            actual_key = field

        # Find all placeholders and replace them.
        def _replacer(m: re.Match) -> str:
            placeholder = m.group(1)
            val = _get_field_value(pv, placeholder)
            return val if val is not None else ""

        pv[actual_key] = re.sub(r"\{([^}]+)\}", _replacer, template)
    return products


def _conditional(products: list[dict], rule: dict) -> list[dict]:
    """Apply a sub-rule only to products matching a condition."""
    condition = rule.get("condition", {})
    then_rule = rule.get("then", {})
    if not condition or not then_rule:
        return products

    for p in products:
        pv = p.get("product_value", {})
        if _evaluate_condition(pv, condition):
            # Apply the then-rule to just this single product.
            _apply_rule([p], then_rule)
    return products


def _regex_replace(products: list[dict], rule: dict) -> list[dict]:
    """Replace text matching a regex pattern in product_value[field]."""
    field = rule.get("field", "")
    pattern = rule.get("pattern", "")
    replacement = rule.get("replacement", "")
    try:
        compiled = re.compile(pattern)
    except re.error:
        return products

    for p in products:
        pv = p.get("product_value", {})
        actual_key = _find_actual_key(pv, field)
        if actual_key is not None and pv[actual_key] is not None:
            pv[actual_key] = compiled.sub(replacement, str(pv[actual_key]))
    return products


def _field_merge(products: list[dict], rule: dict) -> list[dict]:
    """Concatenate values from multiple fields into a target field."""
    target = rule.get("target", "")
    fields = rule.get("fields", [])
    separator = rule.get("separator", " ")
    for p in products:
        pv = p.get("product_value", {})
        parts = []
        for f in fields:
            val = _get_field_value(pv, f)
            parts.append(val if val is not None else "")
        actual_key = _find_actual_key(pv, target)
        if actual_key is None:
            actual_key = target
        pv[actual_key] = separator.join(parts)
    return products


def _set_value(products: list[dict], rule: dict) -> list[dict]:
    """Set a field to a fixed value for all products."""
    field = rule.get("field", "")
    value = rule.get("value", "")
    for p in products:
        pv = p.get("product_value", {})
        actual_key = _find_actual_key(pv, field)
        if actual_key is None:
            actual_key = field
        pv[actual_key] = value
    return products


def _copy_field(products: list[dict], rule: dict) -> list[dict]:
    """Copy value from one field to another."""
    source = rule.get("source", "")
    target = rule.get("target", "")
    for p in products:
        pv = p.get("product_value", {})
        val = _get_field_value(pv, source)
        actual_key = _find_actual_key(pv, target)
        if actual_key is None:
            actual_key = target
        pv[actual_key] = val if val is not None else ""
    return products


def _description_template(products: list[dict], rule: dict) -> list[dict]:
    """Replace a field value with a template. Placeholders {key} are resolved from product_value."""
    field = rule.get("field", "desc")
    template = rule.get("template", "")
    for p in products:
        pv = p.get("product_value", {})
        result = template
        for key, val in pv.items():
            if isinstance(val, str):
                result = result.replace(f"{{{key}}}", val.strip())
        # Remove unresolved placeholders
        result = re.sub(r"\{[^}]+\}", "", result)
        # Clean double spaces
        result = re.sub(r"  +", " ", result).strip()
        pv[field] = result
    return products
