import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import is_ai_available, rewrite_descriptions_bulk


def test_ai_not_available_without_key():
    with patch.dict("os.environ", {}, clear=True):
        # Remove ANTHROPIC_API_KEY if present
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        assert is_ai_available() is False


def test_ai_available_with_key():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        assert is_ai_available() is True


@pytest.mark.asyncio
async def test_bulk_rewrite_without_api_key():
    """Without API key, descriptions should remain unchanged."""
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        products = [
            {"id": 1, "product_name": "Test", "product_value": {"desc": "Original description"}},
        ]
        results = await rewrite_descriptions_bulk(products, "ceneo", limit=1)
        assert len(results) == 1
        assert results[0]["original"] == "Original description"
        assert results[0]["changed"] is False


@pytest.mark.asyncio
async def test_bulk_rewrite_skips_empty_description():
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        products = [
            {"id": 1, "product_name": "Test", "product_value": {"name": "No desc"}},
        ]
        results = await rewrite_descriptions_bulk(products, "ceneo", limit=1)
        assert len(results) == 0


@pytest.mark.asyncio
async def test_bulk_rewrite_respects_limit():
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        products = [
            {"id": i, "product_name": f"P{i}", "product_value": {"desc": f"Desc {i}"}}
            for i in range(20)
        ]
        results = await rewrite_descriptions_bulk(products, "ceneo", limit=5)
        assert len(results) == 5
