"""User models for authentication."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.sql import func

from ..models.prompt import Base


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


class UserORM(Base):
    __tablename__ = "users"
    id = Column(SA_UUID(as_uuid=True), primary_key=True, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    clerk_user_id = Column(String(255), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
