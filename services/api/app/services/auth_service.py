"""Authentication service utilities."""
from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import UUID, uuid4

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings
from app.models.user import User

SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

_serializer = URLSafeTimedSerializer(settings.AUTH_SIGNING_SECRET, salt="session")
_users: Dict[UUID, User] = {}


def get_or_create_user(email: str, name: str | None = None, avatar_url: str | None = None) -> User:
    """Return an existing user or create a new one."""
    for user in _users.values():
        if user.email == email:
            user.last_login_at = datetime.utcnow()
            return user
    user = User(
        id=uuid4(),
        email=email,
        name=name,
        avatar_url=avatar_url,
        created_at=datetime.utcnow(),
        last_login_at=datetime.utcnow(),
    )
    _users[user.id] = user
    return user


def get_user_by_id(user_id: UUID) -> User | None:
    """Retrieve a user by identifier."""
    return _users.get(user_id)


def create_session(user_id: UUID) -> str:
    """Create a signed session token for a user."""
    return _serializer.dumps({"uid": str(user_id)})


def verify_session(token: str) -> UUID | None:
    """Verify a signed session token and return the user id."""
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return UUID(data["uid"])
    except (BadSignature, SignatureExpired, KeyError):
        return None


def generate_csrf_token() -> str:
    """Generate a CSRF token for client use."""
    import secrets

    return secrets.token_urlsafe(32)
