"""Authentication service utilities."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict
from uuid import UUID, uuid4

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import UserORM, UserIdentityORM, AuthProvider

import secrets

SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

_serializer = URLSafeTimedSerializer(settings.AUTH_SIGNING_SECRET, salt="session")


def get_or_create_user(
    db: Session,
    *,
    email: str,
    name: str | None = None,
    avatar_url: str | None = None,
    provider: AuthProvider,
    provider_user_id: str,
    access_token_encrypted: str | None = None,
    refresh_token_encrypted: str | None = None,
    expires_at: datetime | None = None,
) -> UserORM:
    """Return an existing user or create a new one, and upsert identity."""
    # Try to find identity
    identity = db.query(UserIdentityORM).filter_by(
        provider=provider, provider_user_id=provider_user_id
    ).first()
    if identity:
        # Update tokens if changed
        identity.access_token_encrypted = access_token_encrypted
        identity.refresh_token_encrypted = refresh_token_encrypted
        identity.expires_at = expires_at
        identity.updated_at = datetime.now(timezone.utc)
        identity.user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        return identity.user
    # Try to find user by email
    user = db.query(UserORM).filter_by(email=email).first()
    if not user:
        user = UserORM(
            id=uuid4(),
            email=email,
            name=name,
            avatar_url=avatar_url,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.flush()  # assign PK
    # Create identity
    identity = UserIdentityORM(
        id=uuid4(),
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token_encrypted=access_token_encrypted,
        refresh_token_encrypted=refresh_token_encrypted,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(identity)
    db.commit()
    return user


def get_user_by_id(db: Session, user_id: UUID) -> UserORM | None:
    """Retrieve a user by identifier from the database."""
    return db.query(UserORM).filter_by(id=user_id).first()


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

    return secrets.token_urlsafe(32)
