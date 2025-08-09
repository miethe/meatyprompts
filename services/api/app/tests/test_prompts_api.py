import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.models.prompt import Prompt


@pytest.fixture
def sample_prompt() -> Prompt:
    return Prompt(
        id=uuid.uuid4(),
        prompt_id=uuid.uuid4(),
        version="1",
        title="t",
        body="b",
        use_cases=["u"],
        access_control="private",
        target_models=[],
        providers=[],
        integrations=[],
        category=None,
        complexity=None,
        audience=None,
        status=None,
        input_schema=None,
        output_format=None,
        llm_parameters=None,
        success_metrics=None,
        sample_input=None,
        sample_output=None,
        related_prompt_ids=None,
        link=None,
        tags=["tag"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    """Return an authenticated HTTP client."""
    async with AsyncClient(app=app, base_url="https://test") as ac:
        await ac.get("/auth/github/callback")
        yield ac


@pytest.mark.asyncio
async def test_create_prompt_success(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _create_prompt(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr("app.api.prompts.prompt_service.create_prompt", _create_prompt)
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post("/api/v1/prompts", json=payload, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "t"
    assert data["tags"] == ["tag"]


@pytest.mark.asyncio
async def test_create_prompt_validation_error(monkeypatch, auth_client: AsyncClient):
    def _create_prompt(*args, **kwargs):
        raise ValueError("bad data")

    monkeypatch.setattr("app.api.prompts.prompt_service.create_prompt", _create_prompt)
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post("/api/v1/prompts", json=payload, headers=headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_prompts(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _list_prompts(*args, **kwargs):
        return [sample_prompt]

    monkeypatch.setattr("app.api.prompts.prompt_service.list_prompts", _list_prompts)
    resp = await auth_client.get("/api/v1/prompts?model=gpt-4o")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "t"


@pytest.mark.asyncio
async def test_get_prompt_by_id(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _get_prompt_by_id(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.get_prompt_by_id", _get_prompt_by_id
    )
    resp = await auth_client.get(f"/api/v1/prompts/{sample_prompt.prompt_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "t"


@pytest.mark.asyncio
async def test_get_prompt_by_id_not_found(monkeypatch, auth_client: AsyncClient):
    def _get_prompt_by_id(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.get_prompt_by_id", _get_prompt_by_id
    )
    resp = await auth_client.get(f"/api/v1/prompts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _update_prompt(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.update_prompt", _update_prompt
    )
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.put(
        f"/api/v1/prompts/{sample_prompt.prompt_id}", json=payload, headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "t"


@pytest.mark.asyncio
async def test_update_prompt_not_found(monkeypatch, auth_client: AsyncClient):
    def _update_prompt(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.update_prompt", _update_prompt
    )
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.put(
        f"/api/v1/prompts/{uuid.uuid4()}", json=payload, headers=headers
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt_empty_body(monkeypatch, auth_client: AsyncClient):
    def _update_prompt(*args, **kwargs):
        return None  # should not be called

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.update_prompt", _update_prompt
    )
    payload = {
        "title": "t",
        "body": "",
        "use_cases": ["u"],
        "access_control": "private",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.put(
        f"/api/v1/prompts/{uuid.uuid4()}", json=payload, headers=headers
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_prompt(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _duplicate_prompt(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.duplicate_prompt", _duplicate_prompt
    )
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post(
        f"/api/v1/prompts/{sample_prompt.prompt_id}/duplicate",
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "t"


@pytest.mark.asyncio
async def test_duplicate_prompt_not_found(monkeypatch, auth_client: AsyncClient):
    def _duplicate_prompt(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.duplicate_prompt", _duplicate_prompt
    )
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post(
        f"/api/v1/prompts/{uuid.uuid4()}/duplicate",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_prompt_unauthenticated(monkeypatch):
    def _duplicate_prompt(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.duplicate_prompt", _duplicate_prompt
    )
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.post(f"/api/v1/prompts/{uuid.uuid4()}/duplicate")
    assert resp.status_code == 401
