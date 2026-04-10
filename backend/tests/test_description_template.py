from app.services.rules_engine import apply_rules


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_description_template_basic():
    products = [_product({"name": "Folia", "brand": "Lite Solar", "desc": "Opis oryginalny"})]
    rules = [{"type": "description_template", "field": "desc", "template": "Kup {name} marki {brand}!"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Kup Folia marki Lite Solar!"


def test_description_template_missing_placeholder():
    products = [_product({"name": "Folia"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} - {brand}"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Folia -"


def test_description_template_with_at_prefix():
    products = [_product({"@price": "49.99", "name": "Produkt"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} za {@price} zl"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Produkt za 49.99 zl"


def test_description_template_cleans_double_spaces():
    products = [_product({"name": "Folia"})]
    rules = [{"type": "description_template", "field": "desc", "template": "{name}  {missing}  koniec"}]
    result = apply_rules(products, rules)
    assert "  " not in result[0]["product_value"]["desc"]


def test_description_template_default_field():
    products = [_product({"name": "Test"})]
    rules = [{"type": "description_template", "template": "{name} opis"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "Test opis"


def test_description_template_multiple_products():
    products = [
        _product({"name": "A", "cat": "X"}),
        _product({"name": "B", "cat": "Y"}),
    ]
    rules = [{"type": "description_template", "field": "desc", "template": "{name} w {cat}"}]
    result = apply_rules(products, rules)
    assert result[0]["product_value"]["desc"] == "A w X"
    assert result[1]["product_value"]["desc"] == "B w Y"
