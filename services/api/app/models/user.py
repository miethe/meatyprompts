"""User models for authentication."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..models.prompt import Base


class AuthProvider(str, enum.Enum):
    github = "github"
    magic = "magic"
    # Add more providers as needed


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
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class UserIdentityORM(Base):
    __tablename__ = "user_identities"
    id = Column(SA_UUID(as_uuid=True), primary_key=True, nullable=False)
    user_id = Column(SA_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(SAEnum(AuthProvider), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token_encrypted = Column(String(255), nullable=True)
    refresh_token_encrypted = Column(String(255), nullable=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserORM", backref="identities")

    __table_args__ = (
        # Unique constraint: one identity per provider per user
        # And unique provider_user_id per provider
        {
            "sqlite_autoincrement": True,
        },
    )
