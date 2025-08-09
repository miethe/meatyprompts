import json
import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.main import app
from app.models.prompt import Prompt


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="https://test") as ac:
        await ac.get("/auth/github/callback")
        yield ac


@pytest.fixture
def sample_prompt() -> Prompt:
    return Prompt(
        id=uuid.uuid4(),
        prompt_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
        version=1,
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
async def test_import_dry_run(auth_client: AsyncClient):
    payload = json.dumps(
        [
            {
                "title": "t",
                "body": "b",
                "use_cases": "u",
                "access_control": "private",
            }
        ]
    )
    files = {"file": ("prompts.json", payload, "application/json")}
    data = {
        "title": "title",
        "body": "body",
        "use_cases": "use_cases",
        "access_control": "access_control",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post(
        "/api/v1/import", data=data, files=files, headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid_count"] == 1
    assert body["error_count"] == 0


@pytest.mark.asyncio
async def test_import_commit(monkeypatch, auth_client: AsyncClient):
    created: list = []

    def _create_prompt(db, prompt, owner_id):
        created.append(prompt)
        return prompt

    monkeypatch.setattr(
        "app.services.prompt_service.create_prompt", _create_prompt
    )

    payload = json.dumps(
        [
            {
                "title": "t",
                "body": "b",
                "use_cases": "u",
                "access_control": "private",
            }
        ]
    )
    files = {"file": ("prompts.json", payload, "application/json")}
    data = {
        "title": "title",
        "body": "body",
        "use_cases": "use_cases",
        "access_control": "access_control",
    }
    headers = {"X-CSRF-Token": auth_client.cookies.get("csrf_token")}
    resp = await auth_client.post(
        "/api/v1/import?dry_run=false", data=data, files=files, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["created"] == 1
    assert len(created) == 1


@pytest.mark.asyncio
async def test_export(auth_client: AsyncClient, monkeypatch, sample_prompt: Prompt):
    monkeypatch.setattr(
        "app.api.imex.export_service.iter_prompts", lambda *a, **k: iter([sample_prompt])
    )
    resp = await auth_client.get("/api/v1/export")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["title"] == "t"


@pytest.mark.asyncio
async def test_export_requires_auth():
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.get("/api/v1/export")
    assert resp.status_code == 401
