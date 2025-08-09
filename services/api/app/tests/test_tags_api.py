import os
import uuid
import base64
import json
import hmac
import hashlib
from datetime import datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.tag import TagCount
from app.api.deps import get_db
from app.db.session import Base
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
async def test_list_tags(monkeypatch, auth_client: AsyncClient):
    def _top_tags(*args, **kwargs):
        return [TagCount(tag="test", count=2)]

    monkeypatch.setattr("app.api.endpoints.tags.tags_service.top_tags", _top_tags)
    resp = await auth_client.get("/api/v1/tags?query=te")
    assert resp.status_code == 200
    assert resp.json() == [{"tag": "test", "count": 2}]
