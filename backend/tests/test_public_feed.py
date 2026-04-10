import httpx
import pytest

from app.database import engine
from app.main import app


@pytest.fixture(autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_public_feed_not_found():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/feed/nonexistent-uuid.xml")
        assert resp.status_code == 404
