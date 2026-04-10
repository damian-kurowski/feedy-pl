from app.services.validators.facebook import FacebookValidator

def _fb_product(overrides: dict | None = None) -> dict:
    base = {"id": "123", "title": "Test Product", "description": "Product description", "availability": "in stock", "condition": "new", "price": "49.99 PLN", "link": "https://shop.pl/p/123", "image_link": "https://shop.pl/img.jpg", "brand": "TestBrand"}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_fb_product():
    v = FacebookValidator()
    result = v.validate([_fb_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0

def test_fb_missing_brand():
    v = FacebookValidator()
    result = v.validate([_fb_product({"brand": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "brand" for i in errors)

def test_fb_title_too_long():
    v = FacebookValidator()
    result = v.validate([_fb_product({"title": "x" * 250})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "title" for i in warnings)

def test_fb_id_too_long():
    v = FacebookValidator()
    result = v.validate([_fb_product({"id": "x" * 150})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "id" for i in warnings)
