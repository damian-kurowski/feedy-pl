from pathlib import Path

import pytest

from app.services.xml_parser import parse_xml_to_elements

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def gmc_elements():
    raw = (FIXTURES / "sample_gmc.xml").read_bytes()
    return parse_xml_to_elements(raw)


@pytest.fixture
def ceneo_elements():
    raw = (FIXTURES / "sample_ceneo.xml").read_bytes()
    return parse_xml_to_elements(raw)


def _paths(elements: list[dict]) -> set[str]:
    return {e["path"] for e in elements}


class TestParseGmcXmlStructure:
    def test_key_paths_exist(self, gmc_elements):
        paths = _paths(gmc_elements)
        expected = [
            "feed",
            "feed/title",
            "feed/entry",
            "feed/entry/g:id",
            "feed/entry/g:shipping/g:price",
        ]
        for p in expected:
            assert p in paths, f"Missing path: {p}"


class TestParseGmcXmlValues:
    def test_feed_title(self, gmc_elements):
        by_path = {e["path"]: e for e in gmc_elements}
        title = by_path["feed/title"]
        assert title["value"] == "Test Shop"
        assert title["level"] == 2
        assert title["parent_path"] == "feed"
        assert title["is_leaf"] is True


class TestParseGmcXmlLevels:
    def test_levels(self, gmc_elements):
        by_path = {e["path"]: e for e in gmc_elements}
        assert by_path["feed"]["level"] == 1
        assert by_path["feed/entry"]["level"] == 2
        assert by_path["feed/entry/g:id"]["level"] == 3


class TestParseCeneoXml:
    def test_key_paths_exist(self, ceneo_elements):
        paths = _paths(ceneo_elements)
        expected = ["offers", "offers/o", "offers/o/name"]
        for p in expected:
            assert p in paths, f"Missing path: {p}"

    def test_attribute_id_value(self, ceneo_elements):
        by_path = {e["path"]: e for e in ceneo_elements}
        attr = by_path["offers/o/@id"]
        assert attr["value"] == "101"
        assert attr["attribute"] is True


class TestParseXmlDetectsAttributes:
    def test_attribute_elements(self, ceneo_elements):
        attr_elements = [e for e in ceneo_elements if e["attribute"]]
        attr_names = {e["element_name"] for e in attr_elements}
        assert "@id" in attr_names
        assert "@url" in attr_names
        assert "@price" in attr_names
