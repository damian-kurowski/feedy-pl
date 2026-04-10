import uuid

import pytest
import httpx

from app.main import app
from app.database import engine


@pytest.fixture
def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture(autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_and_login(unique_email):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Register
        resp = await client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "testpass123"},
        )
        assert resp.status_code == 201
        tokens = resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        # Login
        resp = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "testpass123"},
        )
        assert resp.status_code == 200
        tokens = resp.json()
        access_token = tokens["access_token"]

        # /me
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == unique_email
        assert data["plan"]["name"] == "Free"


@pytest.mark.asyncio
async def test_register_duplicate_email(unique_email):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "testpass123"},
        )
        resp = await client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "testpass123"},
        )
        assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_wrong_password(unique_email):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "testpass123"},
        )
        resp = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "wrongpassword"},
        )
        assert resp.status_code == 401
