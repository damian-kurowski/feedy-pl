import uuid

import httpx
import pytest

from app.database import engine
from app.main import app


@pytest.fixture
def unique_email():
    return f"feedout-{uuid.uuid4().hex[:12]}@example.com"


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


async def _create_feed_in(client: httpx.AsyncClient) -> int:
    resp = await client.post(
        "/api/feeds-in",
        json={"name": "Source Feed", "source_url": "https://example.com/feed.xml"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_feed_out(authed_client):
    feed_in_id = await _create_feed_in(authed_client)

    resp = await authed_client.post(
        "/api/feeds-out",
        json={"feed_in_id": feed_in_id, "name": "Ceneo Out", "type": "ceneo"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Ceneo Out"
    assert "link_out" in data
    assert len(data["link_out"]) > 0


@pytest.mark.asyncio
async def test_feed_out_plan_limit(authed_client):
    feed_in_id = await _create_feed_in(authed_client)

    # First feed_out should succeed (Free plan allows 1)
    resp = await authed_client.post(
        "/api/feeds-out",
        json={"feed_in_id": feed_in_id, "name": "First Out", "type": "ceneo"},
    )
    assert resp.status_code == 201

    # Second feed_out should fail
    resp = await authed_client.post(
        "/api/feeds-out",
        json={"feed_in_id": feed_in_id, "name": "Second Out", "type": "ceneo"},
    )
    assert resp.status_code == 403
    assert "Upgrade" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_update_structure(authed_client):
    feed_in_id = await _create_feed_in(authed_client)

    resp = await authed_client.post(
        "/api/feeds-out",
        json={"feed_in_id": feed_in_id, "name": "Struct Test", "type": "ceneo"},
    )
    assert resp.status_code == 201
    feed_out_id = resp.json()["id"]

    elements = [
        {
            "sort_key": "001",
            "custom_element": False,
            "path_in": "/items/item/name",
            "level_out": 1,
            "path_out": "/offers/o/name",
            "parent_path_out": "/offers/o",
            "element_name_out": "name",
            "is_leaf": True,
            "attribute": False,
        },
        {
            "sort_key": "002",
            "custom_element": False,
            "path_in": "/items/item/price",
            "level_out": 1,
            "path_out": "/offers/o/price",
            "parent_path_out": "/offers/o",
            "element_name_out": "price",
            "is_leaf": True,
            "attribute": True,
        },
    ]

    resp = await authed_client.put(
        f"/api/feeds-out/{feed_out_id}/structure",
        json=elements,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
