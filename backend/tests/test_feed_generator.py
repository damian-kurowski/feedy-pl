"""Tests for the Ceneo feed generator and templates."""

from lxml import etree

from app.services.feed_generator import generate_allegro_xml, generate_ceneo_xml, generate_gmc_xml, generate_custom_xml
from app.services.templates import CENEO_TEMPLATE


def _sample_products():
    return [
        {"product_value": {
            "g:id": "1", "title": "Płyn do montażu",
            "description": "<b>Opis</b> produktu",
            "g:product_type": "Akcesoria",
            "link": "https://shop.example.com/p/1",
            "g:image_link": "https://shop.example.com/img/1.jpg",
            "g:availability": "in stock", "g:price": "9.5 PLN",
            "g:brand": "EU", "g:gtin": "5901234567890",
        }},
        {"product_value": {
            "g:id": "2", "title": "Folia okienna",
            "description": "Folia na okno",
            "g:product_type": "Folie",
            "link": "https://shop.example.com/p/2",
            "g:image_link": "https://shop.example.com/img/2.jpg",
            "g:availability": "out of stock", "g:price": "29.99 PLN",
            "g:brand": "LiteSolar", "g:gtin": None,
        }},
    ]


def test_ceneo_template_has_required_fields():
    for field in ("id", "name", "price", "url"):
        assert field in CENEO_TEMPLATE


def test_generate_ceneo_xml_valid():
    xml_bytes = generate_ceneo_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    assert root.tag == "offers"
    assert len(root.findall("o")) == 2


def test_generate_ceneo_xml_first_product():
    xml_bytes = generate_ceneo_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    o = root.findall("o")[0]

    assert o.get("id") == "1"
    assert o.get("url") == "https://shop.example.com/p/1"
    assert o.get("price") == "9.50"
    assert o.get("avail") == "1"
    assert o.find("name").text == "Płyn do montażu"
    assert o.find("desc").text == "Opis produktu"
    assert o.find("cat").text == "Akcesoria"


def test_generate_ceneo_xml_images():
    xml_bytes = generate_ceneo_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    o = root.findall("o")[0]
    main_img = o.find("imgs/main")
    assert main_img is not None
    assert main_img.get("url") == "https://shop.example.com/img/1.jpg"


def test_generate_ceneo_xml_attrs():
    xml_bytes = generate_ceneo_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    o = root.findall("o")[0]
    attrs = o.findall("attrs/a")
    attr_map = {a.get("name"): a.text for a in attrs}
    assert attr_map["Producent"] == "EU"
    assert attr_map["EAN"] == "5901234567890"


def test_generate_ceneo_xml_out_of_stock():
    xml_bytes = generate_ceneo_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    o = root.findall("o")[1]
    assert o.get("avail") == "0"
    assert o.get("price") == "29.99"


# ---------------------------------------------------------------------------
# GMC XML tests
# ---------------------------------------------------------------------------

_GMC_NS = {"atom": "http://www.w3.org/2005/Atom", "g": "http://base.google.com/ns/1.0"}


def test_generate_gmc_xml_valid():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entries = root.findall("atom:entry", _GMC_NS)
    assert len(entries) == 2


def test_generate_gmc_xml_fields():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[0]

    gid = entry.find("g:id", _GMC_NS)
    assert gid is not None and gid.text == "1"

    title = entry.find("atom:title", _GMC_NS)
    assert title is not None and "Płyn" in title.text

    price = entry.find("g:price", _GMC_NS)
    assert price is not None and "PLN" in price.text  # GMC keeps currency


def test_generate_gmc_xml_availability_in_stock():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[0]
    avail = entry.find("g:availability", _GMC_NS)
    assert avail is not None and avail.text == "in stock"


def test_generate_gmc_xml_availability_out_of_stock():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[1]
    avail = entry.find("g:availability", _GMC_NS)
    assert avail is not None and avail.text == "out of stock"


def test_generate_gmc_xml_brand_and_gtin():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[0]

    brand = entry.find("g:brand", _GMC_NS)
    assert brand is not None and brand.text == "EU"

    gtin = entry.find("g:gtin", _GMC_NS)
    assert gtin is not None and gtin.text == "5901234567890"


def test_generate_gmc_xml_missing_gtin_omitted():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[1]
    gtin = entry.find("g:gtin", _GMC_NS)
    assert gtin is None  # None gtin should be omitted


def test_generate_gmc_xml_condition_defaults_new():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[0]
    cond = entry.find("g:condition", _GMC_NS)
    assert cond is not None and cond.text == "new"


def test_generate_gmc_xml_product_type():
    xml_bytes = generate_gmc_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    entry = root.findall("atom:entry", _GMC_NS)[0]
    ptype = entry.find("g:product_type", _GMC_NS)
    assert ptype is not None and ptype.text == "Akcesoria"


# ---------------------------------------------------------------------------
# Custom XML tests
# ---------------------------------------------------------------------------


def test_generate_custom_xml_basic():
    structure = [
        {"path_in": "g:id", "element_name_out": "id", "is_leaf": True, "attribute": False, "sort_key": "1"},
        {"path_in": "title", "element_name_out": "name", "is_leaf": True, "attribute": False, "sort_key": "2"},
        {"path_in": "g:price", "element_name_out": "price", "is_leaf": True, "attribute": False, "sort_key": "3"},
    ]
    xml_bytes = generate_custom_xml(_sample_products(), structure)
    root = etree.fromstring(xml_bytes)
    products = root.findall("product")
    assert len(products) == 2
    assert products[0].find("id").text == "1"
    assert products[0].find("name").text == "Płyn do montażu"
    assert products[0].find("price").text == "9.5 PLN"


def test_generate_custom_xml_attributes():
    structure = [
        {"path_in": "g:id", "element_name_out": "@sku", "is_leaf": True, "attribute": True, "sort_key": "1"},
        {"path_in": "title", "element_name_out": "name", "is_leaf": True, "attribute": False, "sort_key": "2"},
    ]
    xml_bytes = generate_custom_xml(_sample_products(), structure)
    root = etree.fromstring(xml_bytes)
    products = root.findall("product")
    assert products[0].get("sku") == "1"
    assert products[0].find("name").text == "Płyn do montażu"


def test_generate_custom_xml_skips_container_rows():
    structure = [
        {"path_in": None, "element_name_out": "offers", "is_leaf": False, "attribute": False, "sort_key": "0"},
        {"path_in": "g:id", "element_name_out": "id", "is_leaf": True, "attribute": False, "sort_key": "1"},
    ]
    xml_bytes = generate_custom_xml(_sample_products(), structure)
    root = etree.fromstring(xml_bytes)
    products = root.findall("product")
    assert len(products) == 2
    assert products[0].find("id").text == "1"


# ---------------------------------------------------------------------------
# Allegro XML tests
# ---------------------------------------------------------------------------


def test_generate_allegro_xml_valid():
    xml_bytes = generate_allegro_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    assert root.tag == "offers"
    offers = root.findall("offer")
    assert len(offers) == 2


def test_generate_allegro_xml_fields():
    xml_bytes = generate_allegro_xml(_sample_products())
    root = etree.fromstring(xml_bytes)
    offer = root.findall("offer")[0]
    assert offer.find("id").text == "1"
    assert "Płyn" in offer.find("name").text
    assert offer.find("price").text == "9.50"
    assert offer.find("availability").text == "available"
    assert offer.find("condition").text == "new"


def test_generate_allegro_xml_category_mapping():
    mapping = {"Akcesoria": "Narzędzia"}
    xml_bytes = generate_allegro_xml(_sample_products(), category_mapping=mapping)
    root = etree.fromstring(xml_bytes)
    offer = root.findall("offer")[0]
    assert offer.find("category").text == "Narzędzia"
