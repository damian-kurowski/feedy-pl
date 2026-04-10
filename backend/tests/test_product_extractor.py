"""Tests for the product extractor service."""

from pathlib import Path

import pytest

from app.services.product_extractor import extract_products

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def gmc_bytes() -> bytes:
    return (FIXTURES / "sample_gmc.xml").read_bytes()


@pytest.fixture
def ceneo_bytes() -> bytes:
    return (FIXTURES / "sample_ceneo.xml").read_bytes()


# --- Google Merchant Center feed ---


def test_extract_gmc_products(gmc_bytes: bytes):
    products = extract_products(gmc_bytes, "feed/entry", "feed/entry/title")
    assert len(products) == 2
    assert products[0]["product_name"] == "Płyn do montażu folii"
    assert products[1]["product_name"] == "Folia okienna przyciemniająca"


def test_extract_gmc_product_values(gmc_bytes: bytes):
    products = extract_products(gmc_bytes, "feed/entry", "feed/entry/title")
    val = products[0]["product_value"]
    assert val["g:id"] == "1"
    assert val["title"] == "Płyn do montażu folii"
    assert val["g:price"] == "9.5 PLN"
    assert val["link"] == "https://shop.example.com/product/1"


def test_extract_gmc_nested_values(gmc_bytes: bytes):
    products = extract_products(gmc_bytes, "feed/entry", "feed/entry/title")
    shipping = products[0]["product_value"]["g:shipping"]
    assert isinstance(shipping, dict)
    assert shipping["g:price"] == "25 PLN"
    assert shipping["g:country"] == "PL"


# --- Ceneo feed ---


def test_extract_ceneo_products(ceneo_bytes: bytes):
    products = extract_products(ceneo_bytes, "offers/o", "offers/o/name")
    assert len(products) == 2
    assert products[0]["product_name"] == "Środek czyszczący"


def test_extract_ceneo_attributes_in_value(ceneo_bytes: bytes):
    products = extract_products(ceneo_bytes, "offers/o", "offers/o/name")
    val = products[0]["product_value"]
    assert val["@id"] == "101"
    assert val["@url"] == "https://shop.example.com/p/101"
    assert val["@price"] == "15.00"
