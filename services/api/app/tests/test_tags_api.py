import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.models.tag import TagCount


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        await ac.get("/auth/github/callback")
        yield ac


@pytest.mark.asyncio
async def test_list_tags(monkeypatch, auth_client: AsyncClient):
    def _top_tags(*args, **kwargs):
        return [TagCount(tag="test", count=2)]

    monkeypatch.setattr("app.api.endpoints.tags.tags_service.top_tags", _top_tags)
    resp = await auth_client.get("/api/v1/tags?query=te")
    assert resp.status_code == 200
    assert resp.json() == [{"tag": "test", "count": 2}]
