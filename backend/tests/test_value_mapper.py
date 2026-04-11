from app.services.value_mapper import apply_value_maps


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_no_maps():
    products = [_product({"status": "in stock"})]
    result = apply_value_maps(products, {})
    assert result[0]["product_value"]["status"] == "in stock"


def test_simple_mapping():
    products = [_product({"status": "in stock"})]
    maps = {"status": {"in stock": "1", "out of stock": "0"}}
    result = apply_value_maps(products, maps)
    assert result[0]["product_value"]["status"] == "1"


def test_no_match_unchanged():
    products = [_product({"status": "unknown"})]
    maps = {"status": {"in stock": "1"}}
    result = apply_value_maps(products, maps)
    assert result[0]["product_value"]["status"] == "unknown"


def test_multiple_fields():
    products = [_product({"status": "in stock", "condition": "new"})]
    maps = {
        "status": {"in stock": "1"},
        "condition": {"new": "nowy", "used": "używany"},
    }
    result = apply_value_maps(products, maps)
    assert result[0]["product_value"]["status"] == "1"
    assert result[0]["product_value"]["condition"] == "nowy"


def test_multiple_products():
    products = [
        _product({"status": "in stock"}),
        _product({"status": "out of stock"}),
    ]
    maps = {"status": {"in stock": "1", "out of stock": "0"}}
    result = apply_value_maps(products, maps)
    assert result[0]["product_value"]["status"] == "1"
    assert result[1]["product_value"]["status"] == "0"
