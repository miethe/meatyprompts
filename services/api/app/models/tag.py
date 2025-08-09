"""Pydantic models for tag suggestions."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TagCount(BaseModel):
    """Represents a tag and its usage count."""

    tag: str = Field(..., description="Tag value")
    count: int = Field(..., description="Number of prompts using the tag")

    model_config = {
        "from_attributes": True,
    }
