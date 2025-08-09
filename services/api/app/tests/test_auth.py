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

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_TEST", "sqlite:///:memory:")
os.environ.setdefault("CLERK_JWT_VERIFICATION_KEY", "test-secret")
os.environ.setdefault("CLERK_WEBHOOK_SECRET", "whsec")

from app.main import app  # noqa: E402
from app.db.session import Base  # noqa: E402
from app.api.deps import get_db  # noqa: E402
from app.models.user import UserORM  # noqa: E402


def _make_token(sub: str, secret: str) -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).rstrip(b"=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).rstrip(b"=")
    sig = base64.urlsafe_b64encode(
        hmac.new(secret.encode(), header + b"." + payload, hashlib.sha256).digest()
    ).rstrip(b"=")
    return f"{header.decode()}.{payload.decode()}.{sig.decode()}"


@pytest_asyncio.fixture
async def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(client: AsyncClient) -> None:
    db = next(get_db())  # type: ignore[misc]
    user = UserORM(
        id=uuid.uuid4(),
        clerk_user_id="user_123",
        email="user@example.com",
        name="User",
        avatar_url=None,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()

    token = _make_token("user_123", os.environ["CLERK_JWT_VERIFICATION_KEY"])
    resp = await client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient) -> None:
    token = "invalid.token.value"
    resp = await client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
