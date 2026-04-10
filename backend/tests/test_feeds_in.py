import uuid

import httpx
import pytest

from app.database import engine
from app.main import app


@pytest.fixture
def unique_email():
    return f"feedin-{uuid.uuid4().hex[:12]}@example.com"


@pytest.fixture(autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()


@pytest.fixture
async def authed_client(unique_email):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "testpass123"},
        )
        assert resp.status_code == 201
        token = resp.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client


@pytest.mark.asyncio
async def test_create_and_list_feed_in(authed_client):
    resp = await authed_client.post(
        "/api/feeds-in",
        json={"name": "Test Feed", "source_url": "https://example.com/feed.xml"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Feed"
    assert data["source_url"] == "https://example.com/feed.xml"
    assert data["fetch_status"] == "pending"
    assert data["active"] is True

    resp = await authed_client.get("/api/feeds-in")
    assert resp.status_code == 200
    feeds = resp.json()
    assert len(feeds) >= 1
    assert any(f["name"] == "Test Feed" for f in feeds)


@pytest.mark.asyncio
async def test_update_feed_in(authed_client):
    resp = await authed_client.post(
        "/api/feeds-in",
        json={"name": "Update Me", "source_url": "https://example.com/feed.xml"},
    )
    assert resp.status_code == 201
    feed_id = resp.json()["id"]

    resp = await authed_client.put(
        f"/api/feeds-in/{feed_id}",
        json={"record_path": "/items/item", "product_name": "item"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["record_path"] == "/items/item"
    assert data["product_name"] == "item"
    assert data["name"] == "Update Me"


@pytest.mark.asyncio
async def test_delete_feed_in(authed_client):
    resp = await authed_client.post(
        "/api/feeds-in",
        json={"name": "Delete Me", "source_url": "https://example.com/feed.xml"},
    )
    assert resp.status_code == 201
    feed_id = resp.json()["id"]

    resp = await authed_client.delete(f"/api/feeds-in/{feed_id}")
    assert resp.status_code == 204

    resp = await authed_client.get(f"/api/feeds-in/{feed_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_feed_in_not_found(authed_client):
    resp = await authed_client.get("/api/feeds-in/99999")
    assert resp.status_code == 404
