from app.services.validators.skapiec import SkapiecValidator

def _skapiec_product(overrides: dict | None = None) -> dict:
    base = {"id": "123", "name": "Test Product", "url": "https://shop.pl/p/123", "price": "49.99", "category": "Elektronika", "image": "https://shop.pl/img.jpg", "description": "Opis produktu", "producer": "TestBrand", "availability": "1"}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_skapiec_product():
    v = SkapiecValidator()
    result = v.validate([_skapiec_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0

def test_skapiec_missing_producer():
    v = SkapiecValidator()
    result = v.validate([_skapiec_product({"producer": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "producer" for i in errors)
