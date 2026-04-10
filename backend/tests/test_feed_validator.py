"""Tests for the validate_feed dispatcher."""
from app.services.validators import validate_feed


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_validate_feed_ceneo():
    products = [_product({"@id": "1", "@url": "https://x.pl", "@price": "10.00", "@avail": "1", "name": "P", "cat": "C", "desc": "D"})]
    result = validate_feed("ceneo", products)
    assert result.platform == "ceneo"
    assert result.total_products == 1
    assert result.quality_score >= 0


def test_validate_feed_gmc():
    products = [_product({
        "g:id": "1", "title": "P", "description": "D", "link": "https://x.pl",
        "g:image_link": "https://x.pl/img.jpg", "g:availability": "in_stock",
        "g:price": "10.00 PLN", "g:condition": "new", "g:brand": "B",
    })]
    result = validate_feed("gmc", products)
    assert result.platform == "gmc"
    assert 0 <= result.quality_score <= 100


def test_validate_feed_unknown_platform():
    result = validate_feed("unknown", [_product({"id": "1"})])
    assert result.quality_score == 100
    assert result.issues == []


def test_validate_feed_empty_products():
    result = validate_feed("ceneo", [])
    assert result.total_products == 0
    assert result.quality_score >= 0
