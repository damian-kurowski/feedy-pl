from app.services.override_service import apply_overrides


def _product(pid: int, pv: dict) -> dict:
    return {"id": pid, "product_value": pv}


def _override(pid: int, fields: dict | None = None, excluded: bool = False) -> dict:
    return {"product_in_id": pid, "field_overrides": fields or {}, "excluded": excluded}


def test_no_overrides():
    products = [_product(1, {"name": "Original"})]
    result = apply_overrides(products, [])
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "Original"


def test_field_override_merges():
    products = [_product(1, {"name": "Original", "price": "10.00"})]
    overrides = [_override(1, {"name": "Changed"})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Changed"
    assert result[0]["product_value"]["price"] == "10.00"


def test_excluded_product_removed():
    products = [_product(1, {"name": "A"}), _product(2, {"name": "B"})]
    overrides = [_override(1, excluded=True)]
    result = apply_overrides(products, overrides)
    assert len(result) == 1
    assert result[0]["product_value"]["name"] == "B"


def test_override_does_not_mutate_original():
    original_pv = {"name": "Original"}
    products = [_product(1, original_pv)]
    overrides = [_override(1, {"name": "Changed"})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Changed"
    assert original_pv["name"] == "Original"


def test_empty_field_overrides_no_change():
    products = [_product(1, {"name": "Same"})]
    overrides = [_override(1, {})]
    result = apply_overrides(products, overrides)
    assert result[0]["product_value"]["name"] == "Same"


def test_multiple_overrides():
    products = [_product(1, {"name": "A"}), _product(2, {"name": "B"}), _product(3, {"name": "C"})]
    overrides = [_override(1, {"name": "A2"}), _override(3, excluded=True)]
    result = apply_overrides(products, overrides)
    assert len(result) == 2
    assert result[0]["product_value"]["name"] == "A2"
    assert result[1]["product_value"]["name"] == "B"
