import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.api.deps import get_current_user, csrf_protect
from app.models.collection import Collection
from app.models.user import UserORM


@pytest.fixture
def sample_collection() -> Collection:
    return Collection(
        id=uuid.uuid4(),
        name="Work",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        count=None,
    )


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        user = UserORM(
            id=uuid.uuid4(),
            email="u@example.com",
            name=None,
            avatar_url=None,
            created_at=datetime.utcnow(),
        )
        app.dependency_overrides[get_current_user] = lambda: user
        app.dependency_overrides[csrf_protect] = lambda: True
        ac.cookies.set("csrf_token", "token")
        yield ac
    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_list_collections(monkeypatch, auth_client: AsyncClient, sample_collection: Collection):
    def _list_collections(*args, **kwargs):
        return [sample_collection]

    monkeypatch.setattr(
        "app.api.collections.collection_service.list_collections", _list_collections
    )
    resp = await auth_client.get("/api/v1/collections")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["name"] == "Work"


@pytest.mark.asyncio
async def test_create_collection_conflict(monkeypatch, auth_client: AsyncClient):
    def _create_collection(*args, **kwargs):
        raise ValueError("exists")

    monkeypatch.setattr(
        "app.api.collections.collection_service.create_collection", _create_collection
    )
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post(
        "/api/v1/collections", json={"name": "Work"}, headers=headers
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_add_prompt_permission_error(monkeypatch, auth_client: AsyncClient):
    def _add_prompt(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(
        "app.api.collections.collection_service.add_prompt", _add_prompt
    )
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    cid, pid = uuid.uuid4(), uuid.uuid4()
    resp = await auth_client.post(
        f"/api/v1/collections/{cid}/prompts",
        json={"prompt_id": str(pid)},
        headers=headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_collections_unauthenticated():
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.get("/api/v1/collections")
    assert resp.status_code == 401
