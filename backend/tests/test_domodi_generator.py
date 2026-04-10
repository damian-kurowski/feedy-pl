from app.services.feed_generator import generate_domodi_xml
from lxml import etree


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_domodi_basic():
    products = [_product({"g:id": "1", "title": "Sukienka", "link": "https://shop.pl/1", "g:price": "199.99 PLN", "g:product_type": "Odziez", "g:image_link": "https://img.pl/1.jpg", "description": "Opis", "g:brand": "Marka", "g:availability": "in_stock"})]
    xml = generate_domodi_xml(products)
    root = etree.fromstring(xml)
    offers = root.findall("offer")
    assert len(offers) == 1
    assert offers[0].find("name").text == "Sukienka"


def test_domodi_fashion_fields():
    products = [_product({"g:id": "1", "title": "Sukienka", "link": "https://shop.pl/1", "g:price": "199.99 PLN", "g:availability": "in_stock", "color": "Czerwony", "size": "M", "material": "Bawelna", "gender": "damskie"})]
    xml = generate_domodi_xml(products)
    root = etree.fromstring(xml)
    offer = root.find("offer")
    assert offer.find("color").text == "Czerwony"
    assert offer.find("size").text == "M"
    assert offer.find("material").text == "Bawelna"
    assert offer.find("gender").text == "damskie"


def test_domodi_empty_products():
    xml = generate_domodi_xml([])
    root = etree.fromstring(xml)
    assert len(root.findall("offer")) == 0
