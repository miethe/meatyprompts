"""User models for authentication."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Pydantic model representing an authenticated user."""

    id: UUID
    email: EmailStr
    name: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {
        "from_attributes": True,
    }
