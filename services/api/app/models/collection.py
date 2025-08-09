"""Collection models and ORM definitions."""
from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, ForeignKey, Index, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.prompt import Base, PromptHeaderORM


_NAME_RE = re.compile(r"^[A-Za-z0-9\-_.&/ ]{1,64}$")


class CollectionBase(BaseModel):
    """Shared properties for collection operations."""

    name: str = Field(..., description="Display name for the collection")

    @validator("name")
    def validate_name(cls, value: str) -> str:
        """Ensure the collection name meets length and character constraints."""
        if value is None or not value.strip():
            raise ValueError("name must not be empty")
        if not _NAME_RE.fullmatch(value.strip()):
            raise ValueError(
                "invalid name: 1-64 characters; letters, numbers, spaces and -_.&/ only"
            )
        return value.strip()


class CollectionCreate(CollectionBase):
    """Payload for creating or renaming a collection."""


class Collection(CollectionBase):
    """Representation of a collection returned from the API."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    count: Optional[int] = Field(default=None, description="Prompt count when requested")

    model_config = {"from_attributes": True}


class CollectionORM(Base):
    """ORM model backing the ``collections`` table."""

    __tablename__ = "collections"
    __table_args__ = (
        Index("ix_collections_owner_name", "owner_id", "name", unique=True),
        Index("ix_collections_owner_updated", "owner_id", "updated_at"),
    )

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        SA_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name = Column(String(64), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    prompts = relationship(
        "CollectionPromptORM",
        back_populates="collection",
        cascade="all, delete-orphan",
    )


class CollectionPromptORM(Base):
    """Bridge table mapping prompts to collections."""

    __tablename__ = "collection_prompts"
    __table_args__ = (
        Index("ix_collection_prompts_prompt", "prompt_id"),
        Index("ix_collection_prompts_collection", "collection_id"),
    )

    collection_id = Column(
        SA_UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    prompt_id = Column(
        SA_UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        primary_key=True,
    )

    collection = relationship("CollectionORM", back_populates="prompts")
    prompt = relationship(PromptHeaderORM)
