from app.services.validators.domodi import DomodiValidator

def _domodi_product(overrides: dict | None = None) -> dict:
    base = {"id": "123", "name": "Sukienka letnia", "url": "https://shop.pl/p/123", "price": "199.99", "image": "https://shop.pl/img.jpg", "category": "Odzież > Sukienki", "producer": "FashionBrand", "availability": "1"}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_domodi_product():
    v = DomodiValidator()
    result = v.validate([_domodi_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0

def test_domodi_missing_color_warning():
    v = DomodiValidator()
    result = v.validate([_domodi_product()])
    color_cov = [c for c in result.field_coverage if c.field == "color"]
    assert len(color_cov) == 1
    assert color_cov[0].filled == 0

def test_domodi_with_fashion_fields():
    v = DomodiValidator()
    product = _domodi_product({"color": "Czerwony", "size": "M", "gender": "damskie", "material": "Bawełna"})
    result = v.validate([product])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0
    assert result.quality_score >= 90
