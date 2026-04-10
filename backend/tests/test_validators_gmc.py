from app.services.validators.gmc import GmcValidator

def _gmc_product(overrides: dict | None = None) -> dict:
    base = {"g:id": "SKU-123", "title": "Test Product", "description": "Product description text here", "link": "https://shop.pl/p/123", "g:image_link": "https://shop.pl/img/123.jpg", "g:availability": "in_stock", "g:price": "49.99 PLN", "g:condition": "new", "g:brand": "TestBrand"}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_gmc_product():
    v = GmcValidator()
    result = v.validate([_gmc_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0

def test_gmc_missing_title():
    v = GmcValidator()
    result = v.validate([_gmc_product({"title": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "title" for i in errors)

def test_gmc_title_too_long():
    v = GmcValidator()
    result = v.validate([_gmc_product({"title": "x" * 200})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "title" and i.rule == "max_length" for i in warnings)

def test_gmc_price_no_currency():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:price": "49.99"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "g:price" for i in errors)

def test_gmc_invalid_availability():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:availability": "maybe"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "g:availability" for i in errors)

def test_gmc_no_brand_no_gtin():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:brand": None, "g:gtin": None})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.rule == "brand_or_gtin" for i in errors)

def test_gmc_gtin_valid():
    v = GmcValidator()
    result = v.validate([_gmc_product({"g:brand": None, "g:gtin": "5901234123457"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert not any(i.rule == "brand_or_gtin" for i in errors)

def test_gmc_missing_google_category_warning():
    v = GmcValidator()
    result = v.validate([_gmc_product()])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "g:google_product_category" for i in warnings)

def test_gmc_description_too_long():
    v = GmcValidator()
    result = v.validate([_gmc_product({"description": "x" * 6000})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.field == "description" and i.rule == "max_length" for i in warnings)
