"""Service functions for user synchronization."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import UserORM


def sync_user_from_clerk_webhook(db: Session, payload: Dict[str, Any]) -> UserORM:
    """Upsert a user record based on Clerk webhook payload.

    Args:
        db: database session.
        payload: Webhook event payload from Clerk.

    Returns:
        The upserted ``UserORM`` instance.
    """
    data = payload.get("data", {})
    clerk_id = data.get("id")
    if clerk_id is None:
        raise ValueError("payload missing data.id")
    email_addresses = data.get("email_addresses", [])
    email = email_addresses[0]["email_address"] if email_addresses else None
    name = data.get("full_name")
    avatar_url = data.get("image_url")

    user = db.query(UserORM).filter_by(clerk_user_id=clerk_id).first()
    if user is None:
        user = UserORM(
            id=uuid4(),
            clerk_user_id=clerk_id,
            email=email or "",
            name=name,
            avatar_url=avatar_url,
            created_at=datetime.now(timezone.utc),
        )
        db.add(user)
    else:
        user.email = email or user.email
        user.name = name
        user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    return user
