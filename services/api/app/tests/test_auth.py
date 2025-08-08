"""Tests for authentication flow."""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_me_requires_auth() -> None:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.get("/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_and_me() -> None:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        await ac.get("/auth/github/callback")
        resp = await ac.get("/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_logout_clears_session() -> None:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        await ac.get("/auth/github/callback")
        resp = await ac.post("/auth/logout")
        assert resp.status_code == 200
        resp2 = await ac.get("/me")
    assert resp2.status_code == 401


@pytest.mark.asyncio
async def test_prompts_protected() -> None:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.get("/api/v1/prompts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_magic_link_disabled() -> None:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.post("/auth/magic-link", json={"email": "a@example.com"})
    assert resp.status_code == 404
