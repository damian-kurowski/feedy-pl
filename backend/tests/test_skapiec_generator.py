from app.services.feed_generator import generate_skapiec_xml
from lxml import etree


def _product(pv: dict) -> dict:
    return {"product_value": pv}


def test_skapiec_basic():
    products = [_product({"g:id": "1", "title": "Produkt", "link": "https://shop.pl/1", "g:price": "49.99 PLN", "g:product_type": "Kat", "g:image_link": "https://img.pl/1.jpg", "description": "Opis", "g:brand": "Marka", "g:availability": "in_stock", "g:gtin": "123"})]
    xml = generate_skapiec_xml(products)
    root = etree.fromstring(xml)
    offers = root.findall("offer")
    assert len(offers) == 1
    assert offers[0].find("id").text == "1"
    assert offers[0].find("name").text == "Produkt"
    assert offers[0].find("price").text == "49.99"
    assert offers[0].find("producer").text == "Marka"
    assert offers[0].find("availability").text == "1"


def test_skapiec_category_mapping():
    products = [_product({"g:id": "1", "title": "P", "link": "https://x.pl", "g:price": "10 PLN", "g:product_type": "Folie", "g:availability": "in_stock"})]
    xml = generate_skapiec_xml(products, category_mapping={"Folie": "Dom > Folie okienne"})
    root = etree.fromstring(xml)
    assert root.find("offer/category").text == "Dom > Folie okienne"


def test_skapiec_empty_products():
    xml = generate_skapiec_xml([])
    root = etree.fromstring(xml)
    assert len(root.findall("offer")) == 0
