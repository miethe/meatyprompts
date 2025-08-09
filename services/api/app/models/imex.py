"""Models for import and export operations."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.prompt import PromptCreate


class ImportMapping(BaseModel):
    """Mapping of source columns to prompt fields."""

    title: str = Field(..., description="Column name for prompt title")
    body: str = Field(..., description="Column name for prompt body")
    use_cases: str = Field(..., description="Column name for use cases")
    access_control: str = Field(
        ..., description="Column name for access control setting"
    )
    tags: Optional[str] = Field(
        default=None, description="Column name for comma separated tags"
    )
    target_models: Optional[str] = Field(
        default=None, description="Column name for comma separated model ids"
    )
    providers: Optional[str] = Field(
        default=None, description="Column name for comma separated providers"
    )
    link: Optional[str] = Field(
        default=None, description="Column name for optional reference link"
    )


class ImportPreviewRow(BaseModel):
    """Represents validation outcome for a single input row."""

    row_index: int = Field(..., description="Zero based index for the row")
    valid: bool = Field(..., description="Whether the row passed validation")
    errors: List[str] | None = Field(
        default=None, description="Validation errors for the row"
    )
    mapped: PromptCreate | None = Field(
        default=None, description="Mapped prompt payload if valid"
    )


class ImportPreview(BaseModel):
    """Preview information returned from a dry run."""

    rows: List[ImportPreviewRow] = Field(
        ..., description="Row level validation information"
    )
    valid_count: int = Field(..., description="Number of valid rows")
    error_count: int = Field(..., description="Number of rows with errors")


class ImportResult(BaseModel):
    """Result summary returned after committing an import."""

    created: int = Field(..., description="Number of prompts created")
    skipped: int = Field(..., description="Number of rows skipped")
    errors: List[str] = Field(
        default_factory=list, description="Errors encountered during commit"
    )
