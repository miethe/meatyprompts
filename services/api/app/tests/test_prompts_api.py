import uuid
from datetime import datetime

import pytest
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


@pytest.mark.asyncio
async def test_create_prompt_success(monkeypatch, sample_prompt):
    def _create_prompt(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr("app.api.prompts.prompt_service.create_prompt", _create_prompt)
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/prompts", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "t"
    assert data["tags"] == ["tag"]


@pytest.mark.asyncio
async def test_create_prompt_validation_error(monkeypatch):
    def _create_prompt(*args, **kwargs):
        raise ValueError("bad data")

    monkeypatch.setattr("app.api.prompts.prompt_service.create_prompt", _create_prompt)
    payload = {
        "title": "t",
        "body": "b",
        "use_cases": ["u"],
        "access_control": "private",
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/prompts", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_prompts(monkeypatch, sample_prompt):
    def _list_prompts(*args, **kwargs):
        return [sample_prompt]

    monkeypatch.setattr("app.api.prompts.prompt_service.list_prompts", _list_prompts)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/prompts?model=gpt-4o")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "t"


@pytest.mark.asyncio
async def test_get_prompt_by_id(monkeypatch, sample_prompt):
    def _get_prompt_by_id(*args, **kwargs):
        return sample_prompt

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.get_prompt_by_id", _get_prompt_by_id
    )
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get(f"/api/v1/prompts/{sample_prompt.prompt_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "t"


@pytest.mark.asyncio
async def test_get_prompt_by_id_not_found(monkeypatch):
    def _get_prompt_by_id(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "app.api.prompts.prompt_service.get_prompt_by_id", _get_prompt_by_id
    )
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get(f"/api/v1/prompts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_prompt(monkeypatch, sample_prompt):
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
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.put(
            f"/api/v1/prompts/{sample_prompt.prompt_id}", json=payload
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "t"


@pytest.mark.asyncio
async def test_update_prompt_not_found(monkeypatch):
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
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.put(f"/api/v1/prompts/{uuid.uuid4()}", json=payload)
    assert resp.status_code == 404
