from app.services.validators.ceneo import CeneoValidator

def _ceneo_product(overrides: dict | None = None) -> dict:
    base = {"@id": "123", "@url": "https://shop.pl/p/123", "@price": "49.99", "@avail": "1", "name": "Test Product", "cat": "Elektronika", "desc": "Opis produktu testowego", "imgs": {"main": {"@url": "https://shop.pl/img.jpg"}}}
    if overrides:
        base.update(overrides)
    return {"product_value": base}

def test_valid_ceneo_product():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    errors = [i for i in result.issues if i.level == "error"]
    assert len(errors) == 0
    assert result.quality_score >= 80

def test_ceneo_missing_id():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@id": None})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@id" for i in errors)

def test_ceneo_missing_price():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": ""})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@price" for i in errors)

def test_ceneo_invalid_price_format():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": "abc"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.rule == "invalid_price" for i in errors)

def test_ceneo_price_with_currency_warns():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@price": "49.99 PLN"})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.rule == "price_has_currency" for i in warnings)

def test_ceneo_invalid_avail():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"@avail": "maybe"})])
    errors = [i for i in result.issues if i.level == "error"]
    assert any(i.field == "@avail" for i in errors)

def test_ceneo_missing_image_warning():
    v = CeneoValidator()
    result = v.validate([_ceneo_product({"imgs": None})])
    warnings = [i for i in result.issues if i.level == "warning"]
    assert any(i.rule == "missing_image" for i in warnings)

def test_ceneo_missing_producer_warning():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    producer_coverage = [c for c in result.field_coverage if c.field == "producer"]
    assert len(producer_coverage) == 1
    assert producer_coverage[0].filled == 0

def test_ceneo_field_coverage():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    assert result.total_products == 1
    id_cov = next(c for c in result.field_coverage if c.field == "@id")
    assert id_cov.filled == 1
    assert id_cov.percent == 100.0

def test_ceneo_quality_score_present():
    v = CeneoValidator()
    result = v.validate([_ceneo_product()])
    assert 0 <= result.quality_score <= 100
    assert result.quality_label in ("Doskonały", "Dobry", "Wymaga poprawy", "Słaby")
