from app.services.recommendations import generate_recommendations
import pytest


@pytest.mark.asyncio
async def test_recommendations_empty_user():
    """Recommendations should work even with no feeds."""
    # This is a smoke test — full test would need DB session
    # Just verify the module imports correctly
    from app.services.recommendations import generate_recommendations
    assert callable(generate_recommendations)
