import os
import base64
import json
import hmac
import hashlib
import uuid
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.prompt import Prompt
from app.services import search_service
from app.db.session import Base
from app.api.deps import get_db
from app.models.user import UserORM

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_TEST", "sqlite:///:memory:")
os.environ.setdefault("CLERK_JWT_VERIFICATION_KEY", "test-secret")
os.environ.setdefault("CLERK_WEBHOOK_SECRET", "whsec")


def _make_token(sub: str, secret: str) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).rstrip(b"=")
    sig = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), header + b"." + payload, hashlib.sha256).digest()
    ).rstrip(b"=")
    return f"{header.decode()}.{payload.decode()}.{sig.decode()}"


@pytest.fixture
def sample_prompt() -> Prompt:
    return Prompt(
        id=uuid.uuid4(),
        prompt_id=uuid.uuid4(),
        owner_id=uuid.uuid4(),
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
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="https://test") as ac:
        db = next(override_get_db())
        user = UserORM(
            id=uuid.uuid4(),
            clerk_user_id="user_123",
            email="u@example.com",
            name=None,
            avatar_url=None,
            created_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        token = _make_token("user_123", os.environ["CLERK_JWT_VERIFICATION_KEY"])
        ac.headers.update({"Authorization": f"Bearer {token}"})
        yield ac

    app.dependency_overrides = {}


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
    resp = await auth_client.post("/api/v1/prompts", json=payload)
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
    resp = await auth_client.post("/api/v1/prompts", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_prompts(monkeypatch, sample_prompt, auth_client: AsyncClient):
    def _list_prompts(*args, **kwargs):
        return {
            "items": [sample_prompt],
            "next_cursor": None,
            "count": 1,
            "total_estimate": None,
        }

    monkeypatch.setattr("app.api.prompts.prompt_service.list_prompts", _list_prompts)
    resp = await auth_client.get("/api/v1/prompts?q=test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"][0]["title"] == "t"


@pytest.mark.asyncio
async def test_search_filters(monkeypatch, sample_prompt, auth_client: AsyncClient):
    captured: dict = {}

    class DummyQuery:
        def all(self):
            return []

    def _build_query(db, filters):
        captured["filters"] = filters
        return DummyQuery()

    monkeypatch.setattr(
        "app.services.prompt_service.search_service.build_query", _build_query
    )

    url = (
        "/api/v1/prompts?q=foo&tags=One&tags=two&favorite=true&archived=false"
        "&target_models=gpt-4&providers=openai&purposes=chat&sort=title_asc&limit=5"
    )
    resp = await auth_client.get(url)
    assert resp.status_code == 200
    filters = captured["filters"]
    assert filters.q == "foo"
    assert filters.tags == ["one", "two"]
    assert filters.favorite is True
    assert filters.archived is False
    assert filters.sort == search_service.SearchSort.title_asc
    assert filters.limit == 5


@pytest.mark.asyncio
async def test_get_prompts_unauthenticated():
    async with AsyncClient(app=app, base_url="https://test") as ac:
        resp = await ac.get("/api/v1/prompts")
    assert resp.status_code == 401


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
