from app.services.rules_engine import apply_rules


def _sample_products():
    return [
        {"product_value": {"title": "Folia okienna", "g:price": "49.99 PLN", "g:image_link": "https://img.jpg", "g:product_type": "Folie"}},
        {"product_value": {"title": "Płyn czyszczący", "g:price": "9.50 PLN", "g:image_link": None, "g:product_type": "Chemia"}},
        {"product_value": {"title": "Rakla montażowa", "g:price": "", "g:image_link": "https://img2.jpg", "g:product_type": "Akcesoria"}},
    ]


def test_filter_exclude():
    products = apply_rules(_sample_products(), [{"type": "filter_exclude", "field": "g:product_type", "value": "Chemia"}])
    assert len(products) == 2
    assert all("Chemia" not in p["product_value"].get("g:product_type", "") for p in products)


def test_filter_include():
    products = apply_rules(_sample_products(), [{"type": "filter_include", "field": "g:product_type", "value": "Folie"}])
    assert len(products) == 1
    assert products[0]["product_value"]["title"] == "Folia okienna"


def test_filter_no_image():
    products = apply_rules(_sample_products(), [{"type": "filter_no_image"}])
    assert len(products) == 2  # removes the one with None image


def test_filter_no_price():
    products = apply_rules(_sample_products(), [{"type": "filter_no_price"}])
    assert len(products) == 2  # removes the one with empty price


def test_modify_prefix():
    products = apply_rules(_sample_products(), [{"type": "modify_prefix", "field": "title", "value": "PROMO: "}])
    assert all(p["product_value"]["title"].startswith("PROMO: ") for p in products)


def test_modify_replace():
    products = apply_rules(_sample_products(), [{"type": "modify_replace", "field": "title", "value": "okienna", "new_value": "na okno"}])
    assert products[0]["product_value"]["title"] == "Folia na okno"


def test_no_rules():
    products = apply_rules(_sample_products(), None)
    assert len(products) == 3


def test_multiple_rules():
    rules = [
        {"type": "filter_no_image"},
        {"type": "modify_prefix", "field": "title", "value": "[OK] "},
    ]
    products = apply_rules(_sample_products(), rules)
    assert len(products) == 2
    assert all(p["product_value"]["title"].startswith("[OK] ") for p in products)


def test_filter_no_image_ceneo_format():
    """Products from Ceneo have imgs as nested dict."""
    products = [
        {"product_value": {"name": "A", "imgs": {"main": {"@url": "https://img.jpg"}}}},
        {"product_value": {"name": "B", "imgs": None}},
        {"product_value": {"name": "C"}},  # no image field at all
    ]
    result = apply_rules(products, [{"type": "filter_no_image"}])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "A"


def test_filter_no_image_skapiec_format():
    """Products from Skapiec use imgurl."""
    products = [
        {"product_value": {"name": "A", "imgurl": "https://img.jpg"}},
        {"product_value": {"name": "B", "imgurl": ""}},
    ]
    result = apply_rules(products, [{"type": "filter_no_image"}])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "A"


def test_filter_no_price_at_format():
    """Products from Ceneo have @price."""
    products = [
        {"product_value": {"name": "A", "@price": "49.99"}},
        {"product_value": {"name": "B", "@price": ""}},
        {"product_value": {"name": "C", "@price": None}},
    ]
    result = apply_rules(products, [{"type": "filter_no_price"}])
    assert len(result) == 1


def test_filter_no_price_plain_field():
    """Products from Skapiec use plain 'price'."""
    products = [
        {"product_value": {"name": "A", "price": "10.00"}},
        {"product_value": {"name": "B", "price": "0"}},
    ]
    result = apply_rules(products, [{"type": "filter_no_price"}])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "A"


def test_filter_exclude_alternative_field():
    """filter_exclude on g:product_type should also match 'cat' field."""
    products = [
        {"product_value": {"name": "A", "cat": "Folie"}},
        {"product_value": {"name": "B", "cat": "Chemia"}},
    ]
    result = apply_rules(products, [{"type": "filter_exclude", "field": "g:product_type", "value": "Chemia"}])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "A"


def test_filter_include_alternative_field():
    """filter_include on title should also match 'name' field."""
    products = [
        {"product_value": {"name": "Folia okienna"}},
        {"product_value": {"name": "Płyn czyszczący"}},
    ]
    result = apply_rules(products, [{"type": "filter_include", "field": "title", "value": "Folia"}])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "Folia okienna"


def test_modify_prefix_alternative_field():
    """modify_prefix on title should work with 'name' field."""
    products = [
        {"product_value": {"name": "Folia"}},
    ]
    result = apply_rules(products, [{"type": "modify_prefix", "field": "title", "value": "PROMO: "}])
    assert result[0]["product_value"]["name"] == "PROMO: Folia"


def test_modify_replace_alternative_field():
    """modify_replace on title should work with 'name' field."""
    products = [
        {"product_value": {"name": "Folia okienna"}},
    ]
    result = apply_rules(products, [{"type": "modify_replace", "field": "title", "value": "okienna", "new_value": "na okno"}])
    assert result[0]["product_value"]["name"] == "Folia na okno"


# --- Title template tests ---


def test_title_template():
    products = [{"product_value": {"title": "Folia", "g:brand": "EU", "g:product_type": "Folie"}}]
    result = apply_rules(products, [{"type": "title_template", "field": "title", "template": "{g:brand} {title} - {g:product_type}"}])
    assert result[0]["product_value"]["title"] == "EU Folia - Folie"


def test_title_template_missing_field():
    products = [{"product_value": {"title": "Folia"}}]
    result = apply_rules(products, [{"type": "title_template", "field": "title", "template": "{g:brand} {title}"}])
    assert result[0]["product_value"]["title"] == " Folia"


# --- Conditional rules tests ---


def test_conditional_gt():
    products = [
        {"product_value": {"title": "A", "g:price": "150 PLN"}},
        {"product_value": {"title": "B", "g:price": "50 PLN"}},
    ]
    rule = {
        "type": "conditional",
        "condition": {"field": "g:price", "operator": "gt", "value": "100"},
        "then": {"type": "modify_prefix", "field": "title", "value": "DROGI: "},
    }
    result = apply_rules(products, [rule])
    assert result[0]["product_value"]["title"] == "DROGI: A"
    assert result[1]["product_value"]["title"] == "B"


def test_conditional_lt():
    products = [
        {"product_value": {"title": "A", "g:price": "150 PLN"}},
        {"product_value": {"title": "B", "g:price": "50 PLN"}},
    ]
    rule = {
        "type": "conditional",
        "condition": {"field": "g:price", "operator": "lt", "value": "100"},
        "then": {"type": "modify_prefix", "field": "title", "value": "TANI: "},
    }
    result = apply_rules(products, [rule])
    assert result[0]["product_value"]["title"] == "A"
    assert result[1]["product_value"]["title"] == "TANI: B"


def test_conditional_contains():
    products = [
        {"product_value": {"title": "Folia okienna", "g:product_type": "Folie"}},
        {"product_value": {"title": "Płyn", "g:product_type": "Chemia"}},
    ]
    rule = {
        "type": "conditional",
        "condition": {"field": "g:product_type", "operator": "contains", "value": "Foli"},
        "then": {"type": "modify_prefix", "field": "title", "value": "[HIT] "},
    }
    result = apply_rules(products, [rule])
    assert result[0]["product_value"]["title"] == "[HIT] Folia okienna"
    assert result[1]["product_value"]["title"] == "Płyn"


def test_conditional_eq():
    products = [
        {"product_value": {"title": "A", "g:condition": "new"}},
        {"product_value": {"title": "B", "g:condition": "used"}},
    ]
    rule = {
        "type": "conditional",
        "condition": {"field": "g:condition", "operator": "eq", "value": "new"},
        "then": {"type": "modify_prefix", "field": "title", "value": "[NEW] "},
    }
    result = apply_rules(products, [rule])
    assert result[0]["product_value"]["title"] == "[NEW] A"
    assert result[1]["product_value"]["title"] == "B"


def test_conditional_is_empty():
    products = [
        {"product_value": {"title": "A", "g:brand": ""}},
        {"product_value": {"title": "B", "g:brand": "EU"}},
    ]
    rule = {
        "type": "conditional",
        "condition": {"field": "g:brand", "operator": "is_empty"},
        "then": {"type": "set_value", "field": "g:brand", "value": "Unknown"},
    }
    result = apply_rules(products, [rule])
    assert result[0]["product_value"]["g:brand"] == "Unknown"
    assert result[1]["product_value"]["g:brand"] == "EU"


# --- Regex replace tests ---


def test_regex_replace():
    products = [{"product_value": {"description": "<b>Bold</b> and <i>italic</i>"}}]
    result = apply_rules(products, [{"type": "regex_replace", "field": "description", "pattern": "<[^>]+>", "replacement": ""}])
    assert result[0]["product_value"]["description"] == "Bold and italic"


def test_regex_replace_invalid_pattern():
    """Invalid regex should not crash, products returned unchanged."""
    products = [{"product_value": {"title": "Test"}}]
    result = apply_rules(products, [{"type": "regex_replace", "field": "title", "pattern": "[invalid", "replacement": ""}])
    assert result[0]["product_value"]["title"] == "Test"


# --- Field merge tests ---


def test_field_merge():
    products = [{"product_value": {"g:brand": "EU", "title": "Folia", "g:product_type": "Folie"}}]
    result = apply_rules(products, [{"type": "field_merge", "target": "title", "fields": ["g:brand", "title", "g:product_type"], "separator": " | "}])
    assert result[0]["product_value"]["title"] == "EU | Folia | Folie"


def test_field_merge_missing_field():
    products = [{"product_value": {"title": "Folia"}}]
    result = apply_rules(products, [{"type": "field_merge", "target": "title", "fields": ["g:brand", "title"], "separator": " - "}])
    assert result[0]["product_value"]["title"] == " - Folia"


# --- Set value tests ---


def test_set_value():
    products = [{"product_value": {"title": "A"}}, {"product_value": {"title": "B"}}]
    result = apply_rules(products, [{"type": "set_value", "field": "g:condition", "value": "new"}])
    assert all(p["product_value"]["g:condition"] == "new" for p in result)


# --- Copy field tests ---


def test_copy_field():
    products = [{"product_value": {"title": "Folia okienna"}}]
    result = apply_rules(products, [{"type": "copy_field", "source": "title", "target": "name"}])
    assert result[0]["product_value"]["name"] == "Folia okienna"
