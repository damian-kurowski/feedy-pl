"""Tests for value transformers."""

import pytest

from app.transformers import format_price, map_availability, strip_currency, strip_html


class TestStripCurrency:
    def test_with_space_and_currency(self):
        assert strip_currency("9.5 PLN") == "9.5"

    def test_with_space_and_currency_longer(self):
        assert strip_currency("29.99 PLN") == "29.99"

    def test_without_space(self):
        assert strip_currency("100PLN") == "100"

    def test_no_currency(self):
        assert strip_currency("9.50") == "9.50"

    def test_none(self):
        assert strip_currency(None) is None

    def test_empty(self):
        assert strip_currency("") == ""


class TestFormatPrice:
    def test_one_decimal(self):
        assert format_price("9.5") == "9.50"

    def test_two_decimals(self):
        assert format_price("29.99") == "29.99"

    def test_integer(self):
        assert format_price("100") == "100.00"

    def test_with_currency(self):
        assert format_price("9.5 PLN") == "9.50"

    def test_none(self):
        assert format_price(None) is None

    def test_empty(self):
        assert format_price("") == ""


class TestMapAvailability:
    def test_in_stock(self):
        assert map_availability("in stock") == "1"

    def test_in_stock_title_case(self):
        assert map_availability("In Stock") == "1"

    def test_in_stock_underscore(self):
        assert map_availability("in_stock") == "1"

    def test_available(self):
        assert map_availability("available") == "1"

    def test_out_of_stock(self):
        assert map_availability("out of stock") == "0"

    def test_out_of_stock_underscore(self):
        assert map_availability("out_of_stock") == "0"

    def test_preorder(self):
        assert map_availability("preorder") == "99"

    def test_pre_order_hyphen(self):
        assert map_availability("pre-order") == "99"

    def test_unknown(self):
        assert map_availability("unknown_value") == "0"

    def test_none(self):
        assert map_availability(None) == "0"


class TestStripHtml:
    def test_bold(self):
        assert strip_html("<b>bold</b> text") == "bold text"

    def test_paragraph(self):
        assert strip_html("<p>paragraph</p>") == "paragraph"

    def test_no_html(self):
        assert strip_html("no html") == "no html"

    def test_complex_html(self):
        assert strip_html('<div class="x"><span>hello</span></div>') == "hello"

    def test_none(self):
        assert strip_html(None) is None

    def test_empty(self):
        assert strip_html("") == ""
