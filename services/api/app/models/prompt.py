"""Prompt models and ORM definitions.

This module defines Pydantic models used for request/response
validation alongside the SQLAlchemy ORM models that persist prompt
metadata.  The schema supports a rich set of governance fields to
facilitate discovery and reuse of prompts.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enum import Enum as PyEnum

from pydantic import BaseModel, Field, validator
from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Index, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as SA_UUID, ENUM
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class PromptAccessControl(str, PyEnum):
    """Enumeration for prompt access policies."""

    private = "private"
    unlisted = "unlisted"


class PromptBase(BaseModel):
    """Shared properties for prompt creation and updates."""

    title: str = Field(..., description="Human readable name for the prompt")
    body: str = Field(..., description="Prompt text to be sent to the model")
    use_cases: List[str] = Field(..., description="List of applicable use cases")
    access_control: PromptAccessControl = Field(
        ..., description="Access policy for the prompt"
    )
    target_models: Optional[List[str]] = Field(default=None, description="LLM models this prompt targets")
    providers: Optional[List[str]] = Field(default=None, description="Model providers")
    integrations: Optional[List[str]] = Field(default=None, description="Tooling integrations")
    category: Optional[str] = None
    complexity: Optional[str] = None
    audience: Optional[str] = None
    status: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_format: Optional[str] = None
    llm_parameters: Optional[Dict[str, Any]] = None
    success_metrics: Optional[Dict[str, Any]] = None
    sample_input: Optional[Dict[str, Any]] = None
    sample_output: Optional[Dict[str, Any]] = None
    related_prompt_ids: Optional[List[UUID]] = None
    link: Optional[str] = None
    tags: Optional[List[str]] = None

    @validator("access_control", pre=True)
    def access_control_lower(cls, v):
        if v is not None:
            return v.lower()
        return v


class PromptCreate(PromptBase):
    """Model used when creating a new prompt version."""


class Prompt(PromptBase):
    """Model returned from API responses representing a prompt version."""

    id: UUID
    prompt_id: UUID
    owner_id: UUID
    version: int
    is_favorite: bool = False
    is_archived: bool = False
    block_count: int = 0
    icon_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class PromptHeaderORM(Base):
    """ORM model for the prompts table containing prompt level fields."""

    __tablename__ = "prompts"
    __table_args__ = (Index("ix_prompts_owner_updated", "owner_id", "updated_at"),)

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(SA_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    is_favorite = Column(Boolean, nullable=False, server_default="false")
    is_archived = Column(Boolean, nullable=False, server_default="false")
    block_count = Column(Integer, nullable=False, server_default="0")
    embedding = Column(Vector(1536), nullable=True)
    icon_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PromptVersionORM(Base):
    """ORM model for individual versions of a prompt."""

    __tablename__ = "prompt_versions"
    __table_args__ = (
        Index("ix_prompt_versions_created_at", "created_at"),
        Index("ix_prompt_versions_prompt_desc", "prompt_id", text("version DESC")),
    )

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(SA_UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=False)
    version = Column(Integer, nullable=False)
    body = Column(String, nullable=False)
    description = Column(String, nullable=True)
    access_control = Column(
        ENUM(PromptAccessControl, name="prompt_access_control"), nullable=False
    )
    target_models = Column(ARRAY(String), nullable=True)
    providers = Column(ARRAY(String), nullable=True)
    integrations = Column(ARRAY(String), nullable=True)
    use_cases = Column(ARRAY(String), nullable=False)
    category = Column(String, nullable=True)
    complexity = Column(String, nullable=True)
    audience = Column(String, nullable=True)
    status = Column(String, nullable=True)
    input_schema = Column(JSONB, nullable=True)
    output_format = Column(String, nullable=True)
    llm_parameters = Column(JSONB, nullable=True)
    success_metrics = Column(JSONB, nullable=True)
    sample_input = Column(JSONB, nullable=True)
    sample_output = Column(JSONB, nullable=True)
    related_prompt_ids = Column(ARRAY(SA_UUID(as_uuid=True)), nullable=True)
    link = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
