from app.services.validators.allegro import AllegroValidator

def _allegro_product(overrides: dict | None = None) -> dict:
    base = {"id": "123", "name": "Test Product", "description": "Product description", "url": "https://shop.pl/p/123", "price": "49.99", "category": "Elektronika", "image": "https://shop.pl/img.jpg", "availability": "available"}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_allegro_product():
    v = AllegroValidator()
    result = v.validate([_allegro_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0

def test_allegro_name_too_long():
    v = AllegroValidator()
    result = v.validate([_allegro_product({"name": "x" * 100})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "name" for i in warnings)

def test_allegro_missing_required():
    v = AllegroValidator()
    result = v.validate([_allegro_product({"name": "", "price": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) >= 2
