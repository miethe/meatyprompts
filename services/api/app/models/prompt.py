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

from pydantic import BaseModel, Field
from sqlalchemy import ARRAY, Column, ForeignKey, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID as SA_UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PromptBase(BaseModel):
    """Shared properties for prompt creation and updates."""

    title: str = Field(..., description="Human readable name for the prompt")
    body: str = Field(..., description="Prompt text to be sent to the model")
    use_cases: List[str] = Field(..., description="List of applicable use cases")
    access_control: str = Field(..., description="Access policy for the prompt")
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


class PromptCreate(PromptBase):
    """Model used when creating a new prompt version."""


class Prompt(PromptBase):
    """Model returned from API responses representing a prompt version."""

    id: UUID
    prompt_id: UUID
    version: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class PromptHeaderORM(Base):
    """ORM model for the prompts table containing prompt level fields."""

    __tablename__ = "prompts"

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
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

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(SA_UUID(as_uuid=True), ForeignKey("prompts.id"), nullable=False)
    version = Column(String, nullable=False)
    body = Column(String, nullable=False)
    description = Column(String, nullable=True)
    access_control = Column(String, nullable=False)
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
